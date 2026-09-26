from datetime import datetime, timezone
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, primary_role_code, user_permission_codes
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    safe_decode,
    verify_password,
)
from app.db.session import get_db
from app.models import (
    AuditLog,
    User,
    AccountStatus,
    Role,
    PlayerProfile,
    PlayerStatus,
    PlayingRole,
    Team,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    RefreshRequest,
    TokenResponse,
    UserPublic,
    MessageOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: User) -> UserPublic:
    team_name = None
    category = None
    player_status = None
    playing_role = None
    if user.player_profile:
        player_status = user.player_profile.status.value
        if user.player_profile.playing_role:
            playing_role = user.player_profile.playing_role.value
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
        playing_role=playing_role,
        last_login=user.last_login_at,
        created_at=user.created_at,
    )


def _issue_tokens(user: User, remember_me: bool = True) -> TokenResponse:
    # Long-lived access when "remember me" so back/refresh stays on portal
    expire_minutes = (
        settings.refresh_token_expire_days * 24 * 60
        if remember_me
        else settings.access_token_expire_minutes
    )
    access = create_access_token(
        user.id,
        extra={"roles": [r.code for r in user.roles]},
        expire_minutes=expire_minutes,
    )
    refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=serialize_user(user),
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    email = str(body.email).strip().lower()
    username = (body.username or email.split("@")[0]).strip().lower()
    username = re.sub(r"[^a-z0-9._-]", "", username) or "player"
    if len(username) < 3:
        username = f"user{username}"

    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=400, detail="Email already registered. Please login.")
    if db.query(User).filter(func.lower(User.username) == username).first():
        # try unique username
        base = username
        n = 1
        while db.query(User).filter(func.lower(User.username) == username).first():
            username = f"{base}{n}"
            n += 1
            if n > 99:
                raise HTTPException(status_code=400, detail="Username unavailable")

    player_role = db.query(Role).filter(Role.code == "player").first()
    if not player_role:
        raise HTTPException(status_code=500, detail="System roles not ready. Contact admin.")

    password_hash = hash_password(body.password)
    user = User(
        username=username,
        email=email,
        full_name=body.full_name.strip(),
        phone=(body.phone or "").strip() or None,
        password_hash=password_hash,
        account_status=AccountStatus.active,
    )
    user.roles = [player_role]
    db.add(user)
    db.flush()

    category = (body.category or "senior").strip().lower()
    if category not in ("senior", "junior"):
        raise HTTPException(status_code=400, detail="Category must be senior or junior")

    role_key = body.playing_role.strip().lower().replace("-", "_").replace(" ", "_")
    role_map = {
        "batsman": PlayingRole.batsman,
        "bowler": PlayingRole.bowler,
        "all_rounder": PlayingRole.all_rounder,
        "allrounder": PlayingRole.all_rounder,
        "wicketkeeper": PlayingRole.wicketkeeper,
        "keeper": PlayingRole.wicketkeeper,
    }
    playing = role_map.get(role_key)
    if not playing:
        raise HTTPException(
            status_code=400,
            detail="Playing role must be batsman, bowler, all_rounder, or wicketkeeper",
        )

    default_slug = "senior-1st-xi" if category == "senior" else "u16"
    slug = (body.team_slug or default_slug).strip().lower()
    team = db.query(Team).filter(Team.slug == slug).first()
    if not team:
        # fallback by category
        teams = db.query(Team).all()
        for t in teams:
            if t.category and t.category.slug == category:
                team = t
                break

    count = db.query(PlayerProfile).count() + 1
    player_code = f"MCC-P-{count:04d}"
    lead = (body.leadership_role or "none").strip().lower()
    allowed_lead = {
        "none",
        "senior_captain",
        "senior_vice_captain",
        "junior_captain",
        "junior_vice_captain",
    }
    if lead not in allowed_lead:
        lead = "none"
    if lead != "none":
        for o in db.query(PlayerProfile).filter(PlayerProfile.leadership_role == lead).all():
            o.leadership_role = "none"
    db.add(
        PlayerProfile(
            user_id=user.id,
            player_code=player_code,
            team_id=team.id if team else None,
            address=(body.address or "").strip() or None,
            jersey_number=body.jersey_number,
            playing_role=playing,
            is_wicketkeeper=playing == PlayingRole.wicketkeeper,
            leadership_role=lead,
            status=PlayerStatus.active,
        )
    )

    db.add(
        AuditLog(
            actor_user_id=user.id,
            action="register",
            entity_type="user",
            entity_id=user.id,
            detail=f"Public signup: {email} / {category} / {playing.value}",
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    # Durable backup (survives Render free-tier disk wipe)
    from app.services.github_user_store import upsert_user

    upsert_user(
        {
            "user_id": user.id,
            "username": username,
            "email": email,
            "full_name": body.full_name.strip(),
            "phone": (body.phone or "").strip() or None,
            "address": (body.address or "").strip() or None,
            "password_hash": password_hash,
            "player_code": player_code,
            "category": category,
            "team_slug": team.slug if team else slug,
            "playing_role": playing.value,
            "jersey_number": body.jersey_number,
        }
    )

    return RegisterResponse(
        message="Account created. Please login with your email and password.",
        email=email,
        username=username,
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. No account? Create one on Sign up.",
        )

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
    return _issue_tokens(user, remember_me=body.remember_me)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = safe_decode(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.get(User, payload.get("sub"))
    if not user or user.account_status != AccountStatus.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return _issue_tokens(user, remember_me=True)


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
