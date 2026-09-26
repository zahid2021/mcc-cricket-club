"""Player portal APIs: profile, avatar, notifications, warnings, selection alerts."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permissions, primary_role_code
from app.core.permissions import ROLE_LABELS
from app.db.session import get_db
from app.models import (
    AuditLog,
    Notification,
    PlayerProfile,
    PlayingRole,
    Team,
    User,
)
from app.schemas.auth import (
    AvatarUpdate,
    MessageOut,
    NotificationOut,
    PlayerDashboard,
    PlayerProfileOut,
    PlayerProfileUpdate,
    SelectionNotify,
    WarningCreate,
)

router = APIRouter(prefix="/portal/player", tags=["player-portal"])

SECTIONS = [
    {"key": "profile", "label": "My Profile", "href": "/portal/player/profile"},
]

ROLE_MAP = {
    "batsman": PlayingRole.batsman,
    "bowler": PlayingRole.bowler,
    "all_rounder": PlayingRole.all_rounder,
    "allrounder": PlayingRole.all_rounder,
    "wicketkeeper": PlayingRole.wicketkeeper,
    "keeper": PlayingRole.wicketkeeper,
}


def _playing_role_label(role: PlayingRole | None) -> str | None:
    if not role:
        return None
    labels = {
        PlayingRole.batsman: "Batsman",
        PlayingRole.bowler: "Bowler",
        PlayingRole.all_rounder: "All-rounder",
        PlayingRole.wicketkeeper: "Wicketkeeper",
    }
    return labels.get(role, role.value)


def _category_name(notif_title: str) -> str:
    t = notif_title.lower()
    if "warning" in t:
        return "warning"
    if "select" in t or "playing xi" in t:
        return "selection"
    if "announce" in t:
        return "announcement"
    return "general"


def build_profile(user: User) -> PlayerProfileOut:
    pp = user.player_profile
    return PlayerProfileOut(
        full_name=user.full_name,
        email=user.email,
        username=user.username,
        phone=user.phone,
        address=pp.address if pp else None,
        profile_picture=user.profile_picture,
        player_code=pp.player_code if pp else None,
        team=pp.team.name if pp and pp.team else None,
        category=pp.team.category.name if pp and pp.team and pp.team.category else None,
        playing_role=_playing_role_label(pp.playing_role) if pp else None,
        jersey_number=pp.jersey_number if pp else None,
        batting_style=pp.batting_style if pp else None,
        bowling_style=pp.bowling_style if pp else None,
        is_wicketkeeper=bool(pp.is_wicketkeeper) if pp else False,
        status=(pp.status.value if pp else "active").upper(),
        emergency_contact=pp.emergency_contact if pp else None,
        date_of_birth=pp.date_of_birth if pp else None,
    )


@router.get("/dashboard", response_model=PlayerDashboard)
def player_dashboard(
    user: User = Depends(require_permissions("portal.player")),
    db: Session = Depends(get_db),
):
    role = primary_role_code(user)
    team = category = playing = None
    status = "active"
    if user.player_profile:
        status = user.player_profile.status.value
        playing = _playing_role_label(user.player_profile.playing_role)
        if user.player_profile.team:
            team = user.player_profile.team.name
            if user.player_profile.team.category:
                category = user.player_profile.team.category.name
    unread = (
        db.query(Notification)
        .filter(
            Notification.recipient_user_id == user.id,
            Notification.is_read.is_(False),
        )
        .count()
    )
    return PlayerDashboard(
        welcome_name=user.full_name,
        role_label=ROLE_LABELS.get(role, role.replace("_", " ").title()),
        playing_role=playing,
        team=team,
        category=category,
        status=status.upper(),
        phone=user.phone,
        profile_picture=user.profile_picture,
        unread_notifications=unread,
        upcoming_match="MCC 1st XI vs City United CC",
        sections=SECTIONS,
    )


@router.get("/profile", response_model=PlayerProfileOut)
def get_profile(user: User = Depends(require_permissions("portal.player"))):
    return build_profile(user)


@router.put("/profile", response_model=PlayerProfileOut)
def update_profile(
    body: PlayerProfileUpdate,
    user: User = Depends(require_permissions("portal.player")),
    db: Session = Depends(get_db),
):
    if body.full_name:
        user.full_name = body.full_name.strip()
    if body.phone is not None:
        user.phone = body.phone.strip() or None
    pp = user.player_profile
    if not pp:
        raise HTTPException(400, "Player profile missing")
    if body.address is not None:
        pp.address = body.address.strip() or None
    if body.emergency_contact is not None:
        pp.emergency_contact = body.emergency_contact.strip() or None
    if body.date_of_birth is not None:
        pp.date_of_birth = body.date_of_birth.strip() or None
    if body.batting_style is not None:
        pp.batting_style = body.batting_style.strip() or None
    if body.bowling_style is not None:
        pp.bowling_style = body.bowling_style.strip() or None
    if body.jersey_number is not None:
        pp.jersey_number = body.jersey_number
    if body.playing_role:
        key = body.playing_role.strip().lower().replace("-", "_").replace(" ", "_")
        role = ROLE_MAP.get(key)
        if not role:
            raise HTTPException(400, "Invalid playing role")
        pp.playing_role = role
        pp.is_wicketkeeper = role == PlayingRole.wicketkeeper
    db.commit()
    db.refresh(user)
    return build_profile(user)


@router.post("/avatar", response_model=PlayerProfileOut)
def upload_avatar(
    body: AvatarUpdate,
    user: User = Depends(require_permissions("portal.player")),
    db: Session = Depends(get_db),
):
    data = body.image_data_url.strip()
    if not data.startswith("data:image/"):
        raise HTTPException(400, "Image must be a data URL (jpg/png/webp)")
    if len(data) > 850_000:
        raise HTTPException(400, "Image too large. Use a smaller photo (under ~600KB).")

    user.profile_picture = data
    db.add(user)
    db.commit()
    db.refresh(user)

    # Durable backup (Render free disk is wiped on restart)
    from app.services.github_user_store import save_avatar, upsert_user

    save_avatar(user.id, data)
    upsert_user(
        {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
        }
    )
    return build_profile(user)


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    filter: str | None = None,
    user: User = Depends(require_permissions("portal.player")),
    db: Session = Depends(get_db),
):
    q = db.query(Notification).filter(Notification.recipient_user_id == user.id)
    rows = q.order_by(Notification.created_at.desc()).limit(100).all()
    out = []
    for n in rows:
        cat = _category_name(n.title)
        if filter and filter != cat and filter != "all":
            continue
        out.append(
            NotificationOut(
                id=n.id,
                title=n.title,
                message=n.message,
                priority=n.priority,
                is_read=n.is_read,
                created_at=n.created_at,
                category=cat,
            )
        )
    return out


@router.post("/notifications/{notification_id}/read", response_model=MessageOut)
def mark_read(
    notification_id: str,
    user: User = Depends(require_permissions("portal.player")),
    db: Session = Depends(get_db),
):
    n = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_user_id == user.id,
        )
        .first()
    )
    if not n:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    return MessageOut(message="Marked as read")


@router.get("/warnings", response_model=list[NotificationOut])
def list_warnings(user: User = Depends(require_permissions("portal.player")), db: Session = Depends(get_db)):
    rows = (
        db.query(Notification)
        .filter(Notification.recipient_user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        NotificationOut(
            id=n.id,
            title=n.title,
            message=n.message,
            priority=n.priority,
            is_read=n.is_read,
            created_at=n.created_at,
            category=_category_name(n.title),
        )
        for n in rows
        if _category_name(n.title) == "warning"
    ]


def _find_player(db: Session, identifier: str) -> User:
    ident = identifier.strip().lower()
    user = (
        db.query(User)
        .filter(or_(func.lower(User.email) == ident, func.lower(User.username) == ident))
        .first()
    )
    if not user:
        raise HTTPException(404, "Player not found")
    return user


@router.post("/staff/warning", response_model=MessageOut)
def issue_warning(
    body: WarningCreate,
    request: Request,
    actor: User = Depends(require_permissions("discipline.issue_warning")),
    db: Session = Depends(get_db),
):
    player = _find_player(db, body.player_email_or_username)
    title = f"WARNING RECEIVED — {body.severity}"
    msg = (
        f"Reason: {body.reason}\n"
        f"Description: {body.description}\n"
        f"Severity: {body.severity}\n"
        f"Issued by: {actor.full_name}\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"Status: Active"
    )
    db.add(
        Notification(
            title=title,
            message=msg,
            sender_user_id=actor.id,
            recipient_user_id=player.id,
            priority="high" if body.severity in ("high", "critical") else "normal",
        )
    )
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="issue_warning",
            entity_type="user",
            entity_id=player.id,
            detail=body.reason,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"Warning sent to {player.full_name}")


@router.post("/staff/selection", response_model=MessageOut)
def notify_selection(
    body: SelectionNotify,
    request: Request,
    actor: User = Depends(require_permissions("selection.manage")),
    db: Session = Depends(get_db),
):
    player = _find_player(db, body.player_email_or_username)
    title = "TEAM SELECTION — You are selected"
    msg = (
        f"Match: {body.match_title}\n"
        f"{body.role_note or 'Selected in Playing XI'}\n"
        f"Selected by: {actor.full_name}\n"
        f"Check My Selection / Notifications in your portal."
    )
    db.add(
        Notification(
            title=title,
            message=msg,
            sender_user_id=actor.id,
            recipient_user_id=player.id,
            priority="high",
        )
    )
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="team_selection_notify",
            entity_type="user",
            entity_id=player.id,
            detail=body.match_title,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"Selection notice sent to {player.full_name}")
