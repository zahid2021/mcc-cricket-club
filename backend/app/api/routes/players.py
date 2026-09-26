"""Public + admin player directory for homepage/sponsors."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from app.db.session import get_db
from app.models import PlayerProfile, PlayerStatus, PlayingRole, User

router = APIRouter(prefix="/players", tags=["players"])


class PlayerCard(BaseModel):
    id: str
    full_name: str
    profile_picture: str | None = None
    playing_role: str | None = None
    phone: str | None = None
    category: str | None = None
    team: str | None = None
    jersey_number: int | None = None
    status: str
    player_code: str | None = None


def _role_label(role: PlayingRole | None) -> str | None:
    if not role:
        return None
    return {
        PlayingRole.batsman: "Batsman",
        PlayingRole.bowler: "Bowler",
        PlayingRole.all_rounder: "All-rounder",
        PlayingRole.wicketkeeper: "Wicketkeeper",
    }.get(role, role.value.replace("_", " ").title())


@router.get("/public", response_model=list[PlayerCard])
def list_public_players(
    category: str | None = Query(None, description="senior or junior"),
    db: Session = Depends(get_db),
):
    """Homepage / sponsors: registered players with photo, role, phone, senior/junior."""
    rows = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .filter(PlayerProfile.status.in_([PlayerStatus.active, PlayerStatus.injured]))
        .all()
    )

    out: list[PlayerCard] = []
    for pp in rows:
        user: User | None = pp.user
        if not user:
            continue
        cat = pp.team.category.name if pp.team and pp.team.category else None
        if category and cat and cat.lower() != category.lower():
            continue
        out.append(
            PlayerCard(
                id=user.id,
                full_name=user.full_name,
                profile_picture=user.profile_picture,
                playing_role=_role_label(pp.playing_role),
                phone=user.phone,
                category=cat,
                team=pp.team.name if pp.team else None,
                jersey_number=pp.jersey_number,
                status=pp.status.value.upper(),
                player_code=pp.player_code,
            )
        )
    out.sort(key=lambda p: p.player_code or "", reverse=True)
    return out
