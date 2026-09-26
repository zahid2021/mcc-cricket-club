from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    remember_me: bool = True


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    username: str | None = Field(None, min_length=3, max_length=80)
    phone: str | None = Field(None, max_length=40)
    address: str | None = Field(None, max_length=500)
    category: str = Field(..., description="senior or junior")
    team_slug: str | None = None
    playing_role: str = Field(..., description="batsman|bowler|all_rounder|wicketkeeper")
    jersey_number: int | None = Field(None, ge=1, le=99)
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    phone: str | None = None
    profile_picture: str | None = None
    account_status: str
    roles: list[str]
    primary_role: str
    permissions: list[str]
    team: str | None = None
    category: str | None = None
    player_status: str | None = None
    playing_role: str | None = None
    last_login: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    message: str


class RegisterResponse(BaseModel):
    message: str
    email: EmailStr
    username: str


class ClubPublic(BaseModel):
    name: str
    short_name: str
    motto: str | None = None
    tagline: str | None = None


class TeamPublic(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    is_active: bool


class PlayerDashboard(BaseModel):
    welcome_name: str
    role_label: str
    playing_role: str | None = None
    team: str | None
    category: str | None = None
    status: str
    phone: str | None = None
    profile_picture: str | None = None
    unread_notifications: int = 0
    upcoming_match: str | None = None
    sections: list[dict]


class PlayerProfileOut(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    phone: str | None = None
    address: str | None = None
    profile_picture: str | None = None
    player_code: str | None = None
    team: str | None = None
    category: str | None = None
    playing_role: str | None = None
    jersey_number: int | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    is_wicketkeeper: bool = False
    status: str
    emergency_contact: str | None = None
    date_of_birth: str | None = None


class PlayerProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200)
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    date_of_birth: str | None = None
    batting_style: str | None = None
    bowling_style: str | None = None
    jersey_number: int | None = Field(None, ge=1, le=99)
    playing_role: str | None = None


class AvatarUpdate(BaseModel):
    image_data_url: str = Field(..., min_length=32, max_length=900_000)


class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    category: str = "general"


class WarningCreate(BaseModel):
    player_email_or_username: str
    reason: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=3, max_length=2000)
    severity: str = "medium"


class SelectionNotify(BaseModel):
    player_email_or_username: str
    match_title: str = Field(..., min_length=3, max_length=200)
    role_note: str | None = "Selected in Playing XI"
