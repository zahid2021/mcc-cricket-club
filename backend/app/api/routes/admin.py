"""Admin APIs: match selection, squad, team add/remove, leadership, discipline."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_permissions
from app.db.session import get_db
from app.models import (
    AuditLog,
    Match,
    MatchSquad,
    Notification,
    PlayerProfile,
    PlayerStatus,
    PlayingRole,
    Team,
    User,
)

router = APIRouter(prefix="/admin", tags=["admin"])

LEADERSHIP_LABELS = {
    "none": None,
    "senior_captain": "Senior Captain",
    "senior_vice_captain": "Senior Vice Captain",
    "junior_captain": "Junior Captain",
    "junior_vice_captain": "Junior Vice Captain",
}

ROLE_LABELS = {
    PlayingRole.batsman: "Batsman",
    PlayingRole.bowler: "Bowler",
    PlayingRole.all_rounder: "All-rounder",
    PlayingRole.wicketkeeper: "Wicketkeeper",
}


def _role_label(role: PlayingRole | None) -> str | None:
    if not role:
        return None
    return ROLE_LABELS.get(role, role.value)


def _leadership_label(code: str | None) -> str | None:
    if not code or code == "none":
        return None
    return LEADERSHIP_LABELS.get(code, code.replace("_", " ").title())


# ── Schemas ──────────────────────────────────────────────────────────


class PlayerAdminOut(BaseModel):
    user_id: str
    profile_id: str
    full_name: str
    username: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    date_of_birth: str | None = None
    profile_picture: str | None = None
    playing_role: str | None = None
    leadership_role: str | None = None
    leadership_label: str | None = None
    category: str | None = None
    team: str | None = None
    team_id: str | None = None
    jersey_number: int | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    status: str
    player_code: str | None = None


class TeamOut(BaseModel):
    id: str
    name: str
    slug: str
    category: str | None = None


class MatchCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    opponent: str = Field(..., min_length=2, max_length=200)
    match_date: str = Field(..., min_length=8, max_length=20)  # YYYY-MM-DD
    match_time: str | None = None
    session: str = Field("day", pattern="^(day|night)$")
    category: str = Field("senior", pattern="^(senior|junior)$")
    team_id: str | None = None
    venue: str | None = None
    notes: str | None = None
    is_published: bool = True
    player_profile_ids: list[str] = Field(default_factory=list)


class MatchUpdate(BaseModel):
    title: str | None = None
    opponent: str | None = None
    match_date: str | None = None
    match_time: str | None = None
    session: str | None = Field(None, pattern="^(day|night)$")
    category: str | None = Field(None, pattern="^(senior|junior)$")
    team_id: str | None = None
    venue: str | None = None
    notes: str | None = None
    status: str | None = Field(None, pattern="^(upcoming|completed|cancelled)$")
    is_published: bool | None = None
    player_profile_ids: list[str] | None = None


class SquadPlayerOut(BaseModel):
    profile_id: str
    full_name: str
    profile_picture: str | None = None
    playing_role: str | None = None
    leadership_label: str | None = None
    jersey_number: int | None = None


class MatchOut(BaseModel):
    id: str
    title: str
    opponent: str
    match_date: str
    match_time: str | None = None
    session: str
    category: str
    team_id: str | None = None
    team: str | None = None
    venue: str | None = None
    status: str
    is_published: bool
    notes: str | None = None
    squad: list[SquadPlayerOut] = Field(default_factory=list)


class PlayerTeamUpdate(BaseModel):
    team_id: str | None = None
    status: str | None = None  # active / inactive / suspended / banned / injured
    leadership_role: str | None = None
    playing_role: str | None = None
    remove_from_team: bool = False


class AdminPlayerProfileUpdate(BaseModel):
    """Admin can open and fully edit any player profile."""
    full_name: str | None = Field(None, min_length=2, max_length=200)
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    date_of_birth: str | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    jersey_number: int | None = Field(None, ge=1, le=99)
    playing_role: str | None = None
    leadership_role: str | None = Field(
        None, pattern="^(none|senior_captain|senior_vice_captain|junior_captain|junior_vice_captain)$"
    )
    team_id: str | None = None
    remove_from_team: bool = False
    status: str | None = None
    profile_picture: str | None = None  # data URL or empty string to clear


class LeadershipUpdate(BaseModel):
    leadership_role: str = Field(..., pattern="^(none|senior_captain|senior_vice_captain|junior_captain|junior_vice_captain)$")


# ── Helpers ───────────────────────────────────────────────────────────


def _player_out(pp: PlayerProfile) -> PlayerAdminOut:
    user = pp.user
    cat = pp.team.category.name if pp.team and pp.team.category else None
    lead = pp.leadership_role or "none"
    return PlayerAdminOut(
        user_id=user.id if user else "",
        profile_id=pp.id,
        full_name=user.full_name if user else "—",
        username=user.username if user else "—",
        email=user.email if user else None,
        phone=user.phone if user else None,
        address=pp.address,
        emergency_contact=pp.emergency_contact,
        date_of_birth=pp.date_of_birth,
        profile_picture=user.profile_picture if user else None,
        playing_role=_role_label(pp.playing_role),
        leadership_role=lead,
        leadership_label=_leadership_label(lead),
        category=cat,
        team=pp.team.name if pp.team else None,
        team_id=pp.team_id,
        jersey_number=pp.jersey_number,
        batting_style=pp.batting_style,
        bowling_style=pp.bowling_style,
        status=pp.status.value.upper(),
        player_code=pp.player_code,
    )


def _match_out(m: Match) -> MatchOut:
    squad: list[SquadPlayerOut] = []
    for row in m.squad or []:
        pp = row.player_profile
        if not pp or not pp.user:
            continue
        squad.append(
            SquadPlayerOut(
                profile_id=pp.id,
                full_name=pp.user.full_name,
                profile_picture=pp.user.profile_picture,
                playing_role=_role_label(pp.playing_role),
                leadership_label=_leadership_label(pp.leadership_role),
                jersey_number=pp.jersey_number,
            )
        )
    squad.sort(key=lambda s: s.full_name.lower())
    return MatchOut(
        id=m.id,
        title=m.title,
        opponent=m.opponent,
        match_date=m.match_date,
        match_time=m.match_time,
        session=m.session,
        category=m.category,
        team_id=m.team_id,
        team=m.team.name if m.team else None,
        venue=m.venue,
        status=m.status,
        is_published=m.is_published,
        notes=m.notes,
        squad=squad,
    )


def _set_squad(db: Session, match: Match, profile_ids: list[str]) -> None:
    db.query(MatchSquad).filter(MatchSquad.match_id == match.id).delete()
    seen: set[str] = set()
    for pid in profile_ids:
        if not pid or pid in seen:
            continue
        seen.add(pid)
        pp = db.get(PlayerProfile, pid)
        if not pp:
            continue
        db.add(MatchSquad(match_id=match.id, player_profile_id=pid))


# ── Players & teams ───────────────────────────────────────────────────


@router.get("/players", response_model=list[PlayerAdminOut])
def list_players_admin(
    category: str | None = Query(None),
    team_id: str | None = Query(None),
    user: User = Depends(require_permissions("players.manage")),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .all()
    )
    out: list[PlayerAdminOut] = []
    for pp in rows:
        if not pp.user:
            continue
        cat = pp.team.category.name if pp.team and pp.team.category else None
        if category and cat and cat.lower() != category.lower():
            continue
        if team_id and pp.team_id != team_id:
            continue
        out.append(_player_out(pp))
    out.sort(key=lambda p: p.full_name.lower())
    return out


@router.get("/teams", response_model=list[TeamOut])
def list_teams_admin(
    user: User = Depends(require_permissions("teams.view")),
    db: Session = Depends(get_db),
):
    teams = db.query(Team).filter(Team.is_active.is_(True)).all()
    return [
        TeamOut(
            id=t.id,
            name=t.name,
            slug=t.slug,
            category=t.category.name if t.category else None,
        )
        for t in teams
    ]


@router.patch("/players/{profile_id}", response_model=PlayerAdminOut)
def update_player_admin(
    profile_id: str,
    body: PlayerTeamUpdate,
    user: User = Depends(require_permissions("players.manage")),
    db: Session = Depends(get_db),
):
    pp = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .filter(PlayerProfile.id == profile_id)
        .first()
    )
    if not pp:
        raise HTTPException(404, "Player not found")

    if body.remove_from_team:
        pp.team_id = None
    elif body.team_id is not None:
        if body.team_id == "":
            pp.team_id = None
        else:
            team = db.get(Team, body.team_id)
            if not team:
                raise HTTPException(400, "Invalid team")
            pp.team_id = team.id

    if body.status:
        try:
            pp.status = PlayerStatus(body.status.lower())
        except ValueError as exc:
            raise HTTPException(400, "Invalid status") from exc

    if body.leadership_role is not None:
        if body.leadership_role not in LEADERSHIP_LABELS:
            raise HTTPException(400, "Invalid leadership role")
        # Only one of each leadership per club — clear previous holders
        if body.leadership_role != "none":
            others = (
                db.query(PlayerProfile)
                .filter(
                    PlayerProfile.leadership_role == body.leadership_role,
                    PlayerProfile.id != pp.id,
                )
                .all()
            )
            for o in others:
                o.leadership_role = "none"
        pp.leadership_role = body.leadership_role

    if body.playing_role:
        key = body.playing_role.strip().lower().replace("-", "_").replace(" ", "_")
        role_map = {
            "batsman": PlayingRole.batsman,
            "bowler": PlayingRole.bowler,
            "all_rounder": PlayingRole.all_rounder,
            "allrounder": PlayingRole.all_rounder,
            "wicketkeeper": PlayingRole.wicketkeeper,
            "keeper": PlayingRole.wicketkeeper,
        }
        role = role_map.get(key)
        if not role:
            raise HTTPException(400, "Invalid playing role")
        pp.playing_role = role
        pp.is_wicketkeeper = role == PlayingRole.wicketkeeper

    db.commit()
    db.refresh(pp)
    return _player_out(pp)


def _apply_playing_role(pp: PlayerProfile, playing_role: str) -> None:
    key = playing_role.strip().lower().replace("-", "_").replace(" ", "_")
    role_map = {
        "batsman": PlayingRole.batsman,
        "bowler": PlayingRole.bowler,
        "all_rounder": PlayingRole.all_rounder,
        "allrounder": PlayingRole.all_rounder,
        "wicketkeeper": PlayingRole.wicketkeeper,
        "keeper": PlayingRole.wicketkeeper,
    }
    role = role_map.get(key)
    if not role:
        raise HTTPException(400, "Invalid playing role")
    pp.playing_role = role
    pp.is_wicketkeeper = role == PlayingRole.wicketkeeper


def _apply_leadership(db: Session, pp: PlayerProfile, leadership_role: str) -> None:
    if leadership_role not in LEADERSHIP_LABELS:
        raise HTTPException(400, "Invalid leadership role")
    if leadership_role != "none":
        others = (
            db.query(PlayerProfile)
            .filter(
                PlayerProfile.leadership_role == leadership_role,
                PlayerProfile.id != pp.id,
            )
            .all()
        )
        for o in others:
            o.leadership_role = "none"
    pp.leadership_role = leadership_role


@router.get("/players/{profile_id}", response_model=PlayerAdminOut)
def get_player_admin(
    profile_id: str,
    user: User = Depends(require_permissions("players.manage")),
    db: Session = Depends(get_db),
):
    """Admin: open any player profile."""
    pp = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .filter(PlayerProfile.id == profile_id)
        .first()
    )
    if not pp or not pp.user:
        raise HTTPException(404, "Player not found")
    return _player_out(pp)


@router.put("/players/{profile_id}/profile", response_model=PlayerAdminOut)
def edit_player_profile_admin(
    profile_id: str,
    body: AdminPlayerProfileUpdate,
    actor: User = Depends(require_permissions("players.manage")),
    db: Session = Depends(get_db),
):
    """Admin: fully edit any player's profile fields / photo."""
    pp = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user), joinedload(PlayerProfile.team))
        .filter(PlayerProfile.id == profile_id)
        .first()
    )
    if not pp or not pp.user:
        raise HTTPException(404, "Player not found")
    u = pp.user

    if body.full_name is not None:
        u.full_name = body.full_name.strip()
    if body.phone is not None:
        u.phone = body.phone.strip() or None
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
        _apply_playing_role(pp, body.playing_role)
    if body.leadership_role is not None:
        _apply_leadership(db, pp, body.leadership_role)
    if body.remove_from_team:
        pp.team_id = None
    elif body.team_id is not None:
        if body.team_id == "":
            pp.team_id = None
        else:
            team = db.get(Team, body.team_id)
            if not team:
                raise HTTPException(400, "Invalid team")
            pp.team_id = team.id
    if body.status:
        try:
            pp.status = PlayerStatus(body.status.lower())
        except ValueError as exc:
            raise HTTPException(400, "Invalid status") from exc
    if body.profile_picture is not None:
        pic = body.profile_picture.strip()
        if pic == "":
            u.profile_picture = None
        elif pic.startswith("data:image/"):
            if len(pic) > 850_000:
                raise HTTPException(400, "Image too large")
            u.profile_picture = pic
        else:
            raise HTTPException(400, "Invalid profile picture")

    db.add(u)
    db.add(pp)
    db.commit()
    db.refresh(pp)

    try:
        from app.services.github_user_store import save_avatar, upsert_user

        upsert_user(
            {
                "user_id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "player_code": pp.player_code,
                "address": pp.address,
                "emergency_contact": pp.emergency_contact,
                "date_of_birth": pp.date_of_birth,
                "jersey_number": pp.jersey_number,
                "batting_style": pp.batting_style,
                "bowling_style": pp.bowling_style,
                "playing_role": pp.playing_role.value if pp.playing_role else None,
                "leadership_role": pp.leadership_role,
                "status": pp.status.value if pp.status else None,
                "team_id": pp.team_id,
            }
        )
        if u.profile_picture:
            save_avatar(u.id, u.profile_picture)
    except Exception as exc:  # noqa: BLE001
        print(f"admin profile backup skipped: {exc}")

    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_edit_player_profile",
            entity_type="player_profile",
            entity_id=pp.id,
            detail=f"Edited profile of {u.full_name}",
        )
    )
    db.commit()
    return _player_out(pp)


@router.delete("/players/{profile_id}")
def delete_player_admin(
    profile_id: str,
    actor: User = Depends(require_permissions("players.manage")),
    db: Session = Depends(get_db),
):
    """Admin: remove player from website (profile + login account)."""
    pp = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user))
        .filter(PlayerProfile.id == profile_id)
        .first()
    )
    if not pp or not pp.user:
        raise HTTPException(404, "Player not found")

    target = pp.user
    if target.id == actor.id:
        raise HTTPException(400, "Apna account delete nahi kar sakte")

    # Never delete club admin / super admin accounts via this tool
    role_codes = {r.code for r in (target.roles or [])}
    if role_codes & {"super_admin", "club_admin"}:
        raise HTTPException(400, "Admin account delete nahi ho sakta")

    name = target.full_name
    email = target.email
    username = target.username
    user_id = target.id

    # Squad rows cascade from profile if FK set; delete explicitly for safety
    db.query(MatchSquad).filter(MatchSquad.player_profile_id == pp.id).delete()
    db.query(Notification).filter(Notification.recipient_user_id == user_id).delete()

    db.delete(pp)
    # Clear association table roles
    target.roles.clear()
    db.delete(target)

    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_delete_player",
            entity_type="user",
            entity_id=user_id,
            detail=f"Deleted player {name} ({username})",
        )
    )
    db.commit()

    try:
        from app.services.github_user_store import remove_user

        remove_user(user_id=user_id, email=email, username=username)
    except Exception as exc:  # noqa: BLE001
        print(f"github remove_user skipped: {exc}")

    return {"message": f"{name} website se remove ho gaya", "deleted_user_id": user_id}


# ── Matches ───────────────────────────────────────────────────────────


@router.get("/matches", response_model=list[MatchOut])
def list_matches_admin(
    user: User = Depends(require_permissions("matches.manage")),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Match)
        .options(
            joinedload(Match.team),
            joinedload(Match.squad).joinedload(MatchSquad.player_profile).joinedload(PlayerProfile.user),
        )
        .order_by(Match.match_date.desc())
        .all()
    )
    return [_match_out(m) for m in rows]


@router.post("/matches", response_model=MatchOut, status_code=201)
def create_match(
    body: MatchCreate,
    user: User = Depends(require_permissions("matches.manage")),
    db: Session = Depends(get_db),
):
    if body.team_id:
        if not db.get(Team, body.team_id):
            raise HTTPException(400, "Invalid team")
    m = Match(
        title=body.title.strip(),
        opponent=body.opponent.strip(),
        match_date=body.match_date.strip(),
        match_time=(body.match_time or "").strip() or None,
        session=body.session,
        category=body.category,
        team_id=body.team_id,
        venue=(body.venue or "").strip() or None,
        notes=(body.notes or "").strip() or None,
        is_published=body.is_published,
        status="upcoming",
        created_by_user_id=user.id,
    )
    db.add(m)
    db.flush()
    _set_squad(db, m, body.player_profile_ids)
    db.commit()
    m = (
        db.query(Match)
        .options(
            joinedload(Match.team),
            joinedload(Match.squad).joinedload(MatchSquad.player_profile).joinedload(PlayerProfile.user),
        )
        .filter(Match.id == m.id)
        .first()
    )
    return _match_out(m)


@router.put("/matches/{match_id}", response_model=MatchOut)
def update_match(
    match_id: str,
    body: MatchUpdate,
    user: User = Depends(require_permissions("matches.manage")),
    db: Session = Depends(get_db),
):
    m = db.get(Match, match_id)
    if not m:
        raise HTTPException(404, "Match not found")
    if body.title is not None:
        m.title = body.title.strip()
    if body.opponent is not None:
        m.opponent = body.opponent.strip()
    if body.match_date is not None:
        m.match_date = body.match_date.strip()
    if body.match_time is not None:
        m.match_time = body.match_time.strip() or None
    if body.session is not None:
        m.session = body.session
    if body.category is not None:
        m.category = body.category
    if body.team_id is not None:
        m.team_id = body.team_id or None
    if body.venue is not None:
        m.venue = body.venue.strip() or None
    if body.notes is not None:
        m.notes = body.notes.strip() or None
    if body.status is not None:
        m.status = body.status
    if body.is_published is not None:
        m.is_published = body.is_published
    if body.player_profile_ids is not None:
        _set_squad(db, m, body.player_profile_ids)
    db.commit()
    m = (
        db.query(Match)
        .options(
            joinedload(Match.team),
            joinedload(Match.squad).joinedload(MatchSquad.player_profile).joinedload(PlayerProfile.user),
        )
        .filter(Match.id == match_id)
        .first()
    )
    return _match_out(m)


@router.delete("/matches/{match_id}")
def delete_match(
    match_id: str,
    user: User = Depends(require_permissions("matches.manage")),
    db: Session = Depends(get_db),
):
    m = db.get(Match, match_id)
    if not m:
        raise HTTPException(404, "Match not found")
    db.delete(m)
    db.commit()
    return {"message": "Match deleted"}


# ── Discipline: warning / ban / suspend / unban ───────────────────────


class DisciplineAction(BaseModel):
    profile_id: str
    reason: str = Field(..., min_length=3, max_length=500)
    description: str | None = Field(None, max_length=2000)
    severity: str = "medium"  # for warnings: low|medium|high


class MessageOut(BaseModel):
    message: str


def _get_profile(db: Session, profile_id: str) -> PlayerProfile:
    pp = (
        db.query(PlayerProfile)
        .options(joinedload(PlayerProfile.user))
        .filter(PlayerProfile.id == profile_id)
        .first()
    )
    if not pp or not pp.user:
        raise HTTPException(404, "Player not found")
    return pp


def _notify(db: Session, *, actor: User, player: User, title: str, message: str, priority: str = "high"):
    db.add(
        Notification(
            title=title,
            message=message,
            sender_user_id=actor.id,
            recipient_user_id=player.id,
            priority=priority,
        )
    )


def _set_discipline(pp: PlayerProfile, dtype: str, reason: str) -> None:
    """Store latest discipline so homepage player card can show it."""
    pp.discipline_type = dtype
    pp.discipline_reason = (reason or "").strip()[:500] or None


@router.post("/discipline/warning", response_model=MessageOut)
def admin_warning(
    body: DisciplineAction,
    request: Request,
    actor: User = Depends(require_permissions("discipline.issue_warning")),
    db: Session = Depends(get_db),
):
    pp = _get_profile(db, body.profile_id)
    player = pp.user
    sev = (body.severity or "medium").lower()
    title = f"WARNING RECEIVED — {sev}"
    msg = (
        f"Reason: {body.reason}\n"
        f"Description: {(body.description or '').strip() or '—'}\n"
        f"Severity: {sev}\n"
        f"Issued by: {actor.full_name} (Admin)\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"Status: Active"
    )
    _set_discipline(pp, "warning", body.reason)
    _notify(db, actor=actor, player=player, title=title, message=msg, priority="high" if sev in ("high", "critical") else "normal")
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_warning",
            entity_type="user",
            entity_id=player.id,
            detail=body.reason,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"Warning sent to {player.full_name}")


@router.post("/discipline/clear-warning", response_model=MessageOut)
def admin_clear_warning(
    body: DisciplineAction,
    request: Request,
    actor: User = Depends(require_permissions("discipline.issue_warning")),
    db: Session = Depends(get_db),
):
    """Remove warning from player + homepage card."""
    pp = _get_profile(db, body.profile_id)
    player = pp.user
    note = (body.reason or "").strip() or "Warning cleared by admin"
    pp.discipline_type = None
    pp.discipline_reason = None
    title = "WARNING CLEARED"
    msg = (
        f"Your club warning has been removed.\n"
        f"Note: {note}\n"
        f"Details: {(body.description or '').strip() or '—'}\n"
        f"By: {actor.full_name} (Admin)\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"Homepage pe warning ab nahi dikhegi."
    )
    _notify(db, actor=actor, player=player, title=title, message=msg, priority="normal")
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_clear_warning",
            entity_type="user",
            entity_id=player.id,
            detail=note,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"Warning cleared for {player.full_name}")


@router.post("/discipline/suspend", response_model=MessageOut)
def admin_suspend(
    body: DisciplineAction,
    request: Request,
    actor: User = Depends(require_permissions("discipline.suspend")),
    db: Session = Depends(get_db),
):
    pp = _get_profile(db, body.profile_id)
    player = pp.user
    pp.status = PlayerStatus.suspended
    _set_discipline(pp, "suspend", body.reason)
    title = "SUSPENDED — Club discipline"
    msg = (
        f"You have been SUSPENDED from MCC activities.\n"
        f"Reason: {body.reason}\n"
        f"Details: {(body.description or '').strip() or '—'}\n"
        f"By: {actor.full_name} (Admin)\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"Contact club admin for review."
    )
    _notify(db, actor=actor, player=player, title=title, message=msg)
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_suspend",
            entity_type="user",
            entity_id=player.id,
            detail=body.reason,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"{player.full_name} suspended")


@router.post("/discipline/ban", response_model=MessageOut)
def admin_ban(
    body: DisciplineAction,
    request: Request,
    actor: User = Depends(require_permissions("discipline.ban")),
    db: Session = Depends(get_db),
):
    from app.models import AccountStatus

    pp = _get_profile(db, body.profile_id)
    player = pp.user
    pp.status = PlayerStatus.banned
    player.account_status = AccountStatus.inactive
    _set_discipline(pp, "ban", body.reason)
    title = "BANNED — Club discipline"
    msg = (
        f"You have been BANNED from Mustafa Cricket Club.\n"
        f"Reason: {body.reason}\n"
        f"Details: {(body.description or '').strip() or '—'}\n"
        f"By: {actor.full_name} (Admin)\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}"
    )
    _notify(db, actor=actor, player=player, title=title, message=msg)
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_ban",
            entity_type="user",
            entity_id=player.id,
            detail=body.reason,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"{player.full_name} banned")


@router.post("/discipline/unban", response_model=MessageOut)
def admin_unban(
    body: DisciplineAction,
    request: Request,
    actor: User = Depends(require_permissions("discipline.ban")),
    db: Session = Depends(get_db),
):
    """Remove ban / suspend — restore active status."""
    from app.models import AccountStatus

    pp = _get_profile(db, body.profile_id)
    player = pp.user
    pp.status = PlayerStatus.active
    player.account_status = AccountStatus.active
    _set_discipline(pp, "unban", body.reason)
    title = "REINSTATED — Ban/Suspend removed"
    msg = (
        f"Your club status has been restored to ACTIVE.\n"
        f"Note: {body.reason}\n"
        f"Details: {(body.description or '').strip() or '—'}\n"
        f"By: {actor.full_name} (Admin)\n"
        f"Date: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"You may use Player Portal again."
    )
    _notify(db, actor=actor, player=player, title=title, message=msg, priority="normal")
    db.add(
        AuditLog(
            actor_user_id=actor.id,
            action="admin_unban",
            entity_type="user",
            entity_id=player.id,
            detail=body.reason,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()
    return MessageOut(message=f"{player.full_name} reinstated (active)")


# ── Public matches (homepage) ─────────────────────────────────────────

public_router = APIRouter(prefix="/matches", tags=["matches-public"])


@public_router.get("/public", response_model=list[MatchOut])
def list_public_matches(db: Session = Depends(get_db)):
    rows = (
        db.query(Match)
        .options(
            joinedload(Match.team),
            joinedload(Match.squad).joinedload(MatchSquad.player_profile).joinedload(PlayerProfile.user),
        )
        .filter(Match.is_published.is_(True), Match.status == "upcoming")
        .order_by(Match.match_date.asc())
        .limit(20)
        .all()
    )
    return [_match_out(m) for m in rows]
