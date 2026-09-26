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
    team: str | None
    status: str
    upcoming_match: str | None = None
    sections: list[str]
