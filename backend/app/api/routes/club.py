from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permissions, primary_role_code
from app.core.permissions import ROLE_LABELS
from app.db.session import get_db
from app.models import Club, Team, User
from app.schemas.auth import ClubPublic, TeamPublic, PlayerDashboard, UserPublic
from app.api.routes.auth import serialize_user

router = APIRouter(tags=["club"])


@router.get("/club", response_model=ClubPublic)
def get_club(db: Session = Depends(get_db)):
    club = db.query(Club).first()
    if not club:
        return ClubPublic(
            name="Mustafa Cricket Club",
            short_name="MCC",
            motto="Play Hard. Stay Humble. Win Together.",
            tagline="One Team. One Dream.",
        )
    return ClubPublic(
        name=club.name,
        short_name=club.short_name,
        motto=club.motto,
        tagline=club.tagline,
    )


@router.get("/teams", response_model=list[TeamPublic])
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).filter(Team.is_active.is_(True)).all()
    return [
        TeamPublic(
            id=t.id,
            name=t.name,
            slug=t.slug,
            category=t.category.name if t.category else "",
            is_active=t.is_active,
        )
        for t in teams
    ]


@router.get("/portal/player/dashboard", response_model=PlayerDashboard)
def player_dashboard(user: User = Depends(require_permissions("portal.player"))):
    role = primary_role_code(user)
    team = None
    status = "active"
    if user.player_profile:
        status = user.player_profile.status.value
        if user.player_profile.team:
            team = user.player_profile.team.name
    return PlayerDashboard(
        welcome_name=user.full_name,
        role_label=ROLE_LABELS.get(role, role.replace("_", " ").title()),
        team=team,
        status=status.upper(),
        upcoming_match="MCC 1st XI vs City United CC",
        sections=[
            "My Profile",
            "My Team",
            "My Statistics",
            "My Matches",
            "My Selection",
            "My Training",
            "My Attendance",
            "My Availability",
            "My Awards",
            "My Notifications",
            "My Warnings",
            "My Disciplinary Status",
            "Club Announcements",
        ],
    )


@router.get("/users/me", response_model=UserPublic)
def users_me(user: User = Depends(get_current_user)):
    return serialize_user(user)
