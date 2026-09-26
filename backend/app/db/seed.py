from sqlalchemy.orm import Session

from app.core.permissions import PERMISSIONS, ROLE_PERMISSION_MAP, ROLE_LABELS
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import (
    Club,
    Permission,
    PlayerProfile,
    PlayingRole,
    PlayerStatus,
    Role,
    Team,
    TeamCategory,
    User,
)


def seed_if_empty() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(Role).count() > 0:
            return

        # Permissions
        perm_by_code: dict[str, Permission] = {}
        for code, desc in PERMISSIONS.items():
            p = Permission(code=code, description=desc)
            db.add(p)
            perm_by_code[code] = p
        db.flush()

        # Roles
        role_by_code: dict[str, Role] = {}
        for code, labels in ROLE_LABELS.items():
            role = Role(code=code, name=labels, description=f"{labels} role")
            codes = ROLE_PERMISSION_MAP.get(code, [])
            role.permissions = [perm_by_code[c] for c in codes if c in perm_by_code]
            db.add(role)
            role_by_code[code] = role
        db.flush()

        club = Club(
            name="Mustafa Cricket Club",
            short_name="MCC",
            motto="Play Hard. Stay Humble. Win Together.",
            tagline="One Team. One Dream.",
            email="info@mustafacc.club",
        )
        db.add(club)
        db.flush()

        senior = TeamCategory(name="Senior", slug="senior")
        junior = TeamCategory(name="Junior", slug="junior")
        db.add_all([senior, junior])
        db.flush()

        teams_spec = [
            ("Senior 1st XI", "senior-1st-xi", senior.id),
            ("Senior 2nd XI", "senior-2nd-xi", senior.id),
            ("Development Team", "development", senior.id),
            ("U19", "u19", junior.id),
            ("U16", "u16", junior.id),
            ("U14", "u14", junior.id),
            ("U12", "u12", junior.id),
        ]
        teams: dict[str, Team] = {}
        for name, slug, cat_id in teams_spec:
            t = Team(club_id=club.id, category_id=cat_id, name=name, slug=slug)
            db.add(t)
            teams[slug] = t
        db.flush()

        admin = User(
            username="admin",
            email="admin@mustafacc.club",
            full_name="Club Administrator",
            phone="+10000000000",
            password_hash=hash_password("Admin@MCC2026"),
        )
        admin.roles = [role_by_code["super_admin"]]
        db.add(admin)

        player = User(
            username="mali",
            email="mali@mustafacc.club",
            full_name="Muhammad Ali",
            phone="+10000000001",
            password_hash=hash_password("Player@MCC2026"),
        )
        player.roles = [role_by_code["player"]]
        db.add(player)
        db.flush()

        db.add(
            PlayerProfile(
                user_id=player.id,
                player_code="MCC-P-0001",
                team_id=teams["senior-1st-xi"].id,
                jersey_number=7,
                playing_role=PlayingRole.all_rounder,
                batting_style="Right-hand bat",
                bowling_style="Right-arm medium",
                is_wicketkeeper=False,
                status=PlayerStatus.active,
            )
        )

        captain = User(
            username="captain",
            email="captain@mustafacc.club",
            full_name="Ahmed Khan",
            password_hash=hash_password("Captain@MCC2026"),
        )
        captain.roles = [role_by_code["captain"], role_by_code["player"]]
        db.add(captain)

        db.commit()
        print("MCC seed complete: admin / mali / captain users created")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
