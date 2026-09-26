import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


class AccountStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    locked = "locked"
    pending = "pending"


class PlayerStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    injured = "injured"
    suspended = "suspended"
    banned = "banned"
    retired = "retired"


class PlayingRole(str, enum.Enum):
    batsman = "batsman"
    bowler = "bowler"
    all_rounder = "all_rounder"
    wicketkeeper = "wicketkeeper"


class LeadershipRole(str, enum.Enum):
    none = "none"
    senior_captain = "senior_captain"
    senior_vice_captain = "senior_vice_captain"
    junior_captain = "junior_captain"
    junior_vice_captain = "junior_vice_captain"


class MatchSession(str, enum.Enum):
    day = "day"
    night = "night"


class MatchStatus(str, enum.Enum):
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions, lazy="selectin"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    profile_picture: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus), default=AccountStatus.active
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship(secondary=user_roles, lazy="selectin")
    player_profile: Mapped["PlayerProfile | None"] = relationship(back_populates="user", uselist=False)


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(200), default="Mustafa Cricket Club")
    short_name: Mapped[str] = mapped_column(String(20), default="MCC")
    motto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TeamCategory(Base):
    __tablename__ = "team_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(80), unique=True)  # Senior / Junior
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    club_id: Mapped[str] = mapped_column(ForeignKey("clubs.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("team_categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped[TeamCategory] = relationship(lazy="selectin")


class PlayerProfile(Base):
    __tablename__ = "player_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    player_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    jersey_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    playing_role: Mapped[PlayingRole | None] = mapped_column(Enum(PlayingRole), nullable=True)
    batting_style: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bowling_style: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_wicketkeeper: Mapped[bool] = mapped_column(Boolean, default=False)
    # Club leadership (alongside batsman/bowler etc.)
    leadership_role: Mapped[str | None] = mapped_column(String(40), nullable=True, default="none")
    status: Mapped[PlayerStatus] = mapped_column(Enum(PlayerStatus), default=PlayerStatus.active)
    # Latest discipline shown on homepage player card
    discipline_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # warning|suspend|ban|unban
    discipline_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped[User] = relationship(back_populates="player_profile")
    team: Mapped[Team | None] = relationship(lazy="selectin")


class Match(Base):
    """Admin-scheduled match shown on homepage with selected playing boys."""

    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(200))
    opponent: Mapped[str] = mapped_column(String(200))
    match_date: Mapped[str] = mapped_column(String(20), index=True)  # YYYY-MM-DD
    match_time: Mapped[str | None] = mapped_column(String(10), nullable=True)  # HH:MM
    session: Mapped[str] = mapped_column(String(10), default="day")  # day | night
    category: Mapped[str] = mapped_column(String(20), default="senior")  # senior | junior
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="upcoming")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    team: Mapped[Team | None] = relationship(lazy="selectin")
    squad: Mapped[list["MatchSquad"]] = relationship(
        back_populates="match", cascade="all, delete-orphan", lazy="selectin"
    )


class MatchSquad(Base):
    __tablename__ = "match_squad"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), index=True)
    player_profile_id: Mapped[str] = mapped_column(
        ForeignKey("player_profiles.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    match: Mapped[Match] = relationship(back_populates="squad")
    player_profile: Mapped[PlayerProfile] = relationship(lazy="selectin")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    sender_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    recipient_user_id: Mapped[str] = mapped_column(String(36), index=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
