from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, primary_role_code, user_permission_codes
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    safe_decode,
    verify_password,
)
from app.db.session import get_db
from app.models import AuditLog, User, AccountStatus
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserPublic, MessageOut

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: User) -> UserPublic:
    team_name = None
    category = None
    player_status = None
    if user.player_profile:
        player_status = user.player_profile.status.value
        if user.player_profile.team:
            team_name = user.player_profile.team.name
            if user.player_profile.team.category:
                category = user.player_profile.team.category.name
    return UserPublic(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        profile_picture=user.profile_picture,
        account_status=user.account_status.value,
        roles=[r.code for r in user.roles],
        primary_role=primary_role_code(user),
        permissions=user_permission_codes(user),
        team=team_name,
        category=category,
        player_status=player_status,
        last_login=user.last_login_at,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ident = body.identifier.strip().lower()
    user = (
        db.query(User)
        .filter(or_(User.username == ident, User.email == ident))
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    now = datetime.now(timezone.utc)
    if user.locked_until and user.locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked. Try again later.",
        )

    if not verify_password(body.password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.rate_limit_login_attempts:
            from datetime import timedelta

            user.locked_until = now + timedelta(seconds=settings.rate_limit_login_window_seconds)
            user.failed_login_attempts = 0
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.account_status != AccountStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    db.add(
        AuditLog(
            actor_user_id=user.id,
            action="login",
            entity_type="user",
            entity_id=user.id,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    access = create_access_token(
        user.id,
        extra={"roles": [r.code for r in user.roles]},
    )
    refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=serialize_user(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = safe_decode(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.get(User, payload.get("sub"))
    if not user or user.account_status != AccountStatus.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    access = create_access_token(user.id, extra={"roles": [r.code for r in user.roles]})
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        user=serialize_user(user),
    )


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return serialize_user(user)


@router.post("/logout", response_model=MessageOut)
def logout(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(
        AuditLog(
            actor_user_id=user.id,
            action="logout",
            entity_type="user",
            entity_id=user.id,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message="Logged out")
