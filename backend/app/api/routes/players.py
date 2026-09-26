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
    email: str | None = None
    username: str | None = None
    profile_picture: str | None = None
    playing_role: str | None = None
    leadership_label: str | None = None
    phone: str | None = None
    address: str | None = None
    category: str | None = None
    team: str | None = None
    jersey_number: int | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    date_of_birth: str | None = None
    status: str
    player_code: str | None = None
    discipline_type: str | None = None  # warning | suspend | ban | unban
    discipline_reason: str | None = None
    discipline_label: str | None = None


def _role_label(role: PlayingRole | None) -> str | None:
    if not role:
        return None
    return {
        PlayingRole.batsman: "Batsman",
        PlayingRole.bowler: "Bowler",
        PlayingRole.all_rounder: "All-rounder",
        PlayingRole.wicketkeeper: "Wicketkeeper",
    }.get(role, role.value.replace("_", " ").title())


def _leadership_label(code: str | None) -> str | None:
    if not code or code == "none":
        return None
    return {
        "senior_captain": "Senior Captain",
        "senior_vice_captain": "Senior Vice Captain",
        "junior_captain": "Junior Captain",
        "junior_vice_captain": "Junior Vice Captain",
    }.get(code, code.replace("_", " ").title())


def _discipline_label(dtype: str | None) -> str | None:
    if not dtype:
        return None
    return {
        "warning": "WARNING",
        "suspend": "SUSPENDED",
        "ban": "BANNED",
        "unban": "REINSTATED",
    }.get(dtype.lower(), dtype.upper())


@router.get("/public", response_model=list[PlayerCard])
def list_public_players(
    category: str | None = Query(None, description="senior or junior"),
    db: Session = Depends(get_db),
):
    """Homepage: players with photo, role, senior/junior + discipline reason if any."""
    rows = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .filter(
            PlayerProfile.status.in_(
                [
                    PlayerStatus.active,
                    PlayerStatus.injured,
                    PlayerStatus.suspended,
                    PlayerStatus.banned,
                ]
            )
        )
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
        dtype = getattr(pp, "discipline_type", None)
        dreason = getattr(pp, "discipline_reason", None)
        out.append(
            PlayerCard(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                username=user.username,
                profile_picture=user.profile_picture,
                playing_role=_role_label(pp.playing_role),
                leadership_label=_leadership_label(pp.leadership_role),
                phone=user.phone,
                address=pp.address,
                category=cat,
                team=pp.team.name if pp.team else None,
                jersey_number=pp.jersey_number,
                batting_style=pp.batting_style,
                bowling_style=pp.bowling_style,
                date_of_birth=pp.date_of_birth,
                status=pp.status.value.upper(),
                player_code=pp.player_code,
                discipline_type=dtype,
                discipline_reason=dreason,
                discipline_label=_discipline_label(dtype),
            )
        )
    out.sort(key=lambda p: p.player_code or "", reverse=True)
    return out
