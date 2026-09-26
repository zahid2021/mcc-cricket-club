from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Club, Team
from app.schemas.auth import ClubPublic, TeamPublic, UserPublic
from app.api.routes.auth import serialize_user
from app.models import User

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


@router.get("/users/me", response_model=UserPublic)
def users_me(user: User = Depends(get_current_user)):
    return serialize_user(user)
