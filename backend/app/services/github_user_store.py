"""Persist registered users + profile photos to GitHub (survives Render free restarts)."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import httpx

REPO = os.getenv("GITHUB_REPO", "zahid2021/mcc-cricket-club")
PATH = os.getenv("GITHUB_USERS_PATH", "data/registered_users.json")
AVATAR_DIR = os.getenv("GITHUB_AVATAR_DIR", "data/avatars")
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def _headers() -> dict[str, str]:
    if not TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _put_file(path: str, content_text: str, message: str) -> bool:
    if not TOKEN:
        print("github_user_store: no GITHUB_TOKEN — skip persist")
        return False
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    encoded = base64.b64encode(content_text.encode("utf-8")).decode("ascii")
    try:
        with httpx.Client(timeout=60) as client:
            sha = None
            existing = client.get(url, headers=_headers())
            if existing.status_code == 200:
                sha = existing.json().get("sha")
            payload: dict[str, Any] = {
                "message": message,
                "content": encoded,
                "branch": "main",
            }
            if sha:
                payload["sha"] = sha
            r = client.put(url, headers=_headers(), json=payload)
            if r.status_code not in (200, 201):
                print(f"github put {path} failed: {r.status_code} {r.text[:300]}")
                return False
            return True
    except Exception as exc:  # noqa: BLE001
        print(f"github put {path} error: {exc}")
        return False


def _get_file(path: str) -> str | None:
    if not TOKEN:
        return None
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    try:
        with httpx.Client(timeout=60) as client:
            r = client.get(url, headers=_headers())
            if r.status_code == 404:
                return None
            r.raise_for_status()
            data = r.json()
            return base64.b64decode(data.get("content", "")).decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"github get {path} error: {exc}")
        return None


def load_users() -> list[dict[str, Any]]:
    raw = _get_file(PATH)
    if not raw:
        return []
    try:
        users = json.loads(raw)
        return users if isinstance(users, list) else []
    except Exception as exc:  # noqa: BLE001
        print(f"github_user_store load failed: {exc}")
        return []


def save_users(users: list[dict[str, Any]]) -> None:
    # Never embed huge profile pictures inside users.json
    slim = []
    for u in users:
        row = {k: v for k, v in u.items() if k != "profile_picture"}
        slim.append(row)
    _put_file(PATH, json.dumps(slim, indent=2, ensure_ascii=False), "chore: sync registered MCC users")


def upsert_user(record: dict[str, Any]) -> None:
    users = load_users()
    email = (record.get("email") or "").lower()
    username = (record.get("username") or "").lower()
    pic = record.pop("profile_picture", None)
    user_id = record.get("user_id")

    merged = False
    for i, u in enumerate(users):
        if u.get("email", "").lower() == email or u.get("username", "").lower() == username:
            users[i] = {**u, **{k: v for k, v in record.items() if v is not None}}
            user_id = users[i].get("user_id") or user_id
            merged = True
            break
    if not merged:
        users.append(record)
    save_users(users)

    if pic and user_id:
        save_avatar(user_id, pic)


def save_avatar(user_id: str, data_url: str) -> bool:
    if not data_url or not data_url.startswith("data:image/"):
        return False
    path = f"{AVATAR_DIR}/{user_id}.txt"
    ok = _put_file(path, data_url, f"chore: save avatar {user_id}")
    if ok:
        print(f"github_user_store: avatar saved for {user_id}")
    return ok


def load_avatar(user_id: str) -> str | None:
    raw = _get_file(f"{AVATAR_DIR}/{user_id}.txt")
    if raw and raw.startswith("data:image/"):
        return raw
    return None


def restore_into_db(db) -> int:
    """Import backed-up users + avatars into SQLAlchemy DB."""
    from app.models import (
        User,
        Role,
        PlayerProfile,
        PlayerStatus,
        PlayingRole,
        Team,
        AccountStatus,
    )

    users = load_users()
    if not users:
        return 0
    player_role = db.query(Role).filter(Role.code == "player").first()
    imported = 0
    updated_pics = 0
    updated_profiles = 0
    role_map = {
        "batsman": PlayingRole.batsman,
        "bowler": PlayingRole.bowler,
        "all_rounder": PlayingRole.all_rounder,
        "wicketkeeper": PlayingRole.wicketkeeper,
    }
    for rec in users:
        email = (rec.get("email") or "").lower().strip()
        username = (rec.get("username") or "").lower().strip()
        if not email or not username or not rec.get("password_hash"):
            continue
        exists = (
            db.query(User)
            .filter((User.email == email) | (User.username == username))
            .first()
        )
        if exists:
            # Restore / refresh profile fields from backup
            if rec.get("full_name") and exists.full_name != rec["full_name"]:
                exists.full_name = rec["full_name"]
                updated_profiles += 1
            if rec.get("phone") is not None and exists.phone != rec.get("phone"):
                exists.phone = rec.get("phone")
                updated_profiles += 1
            pic = load_avatar(exists.id) or (
                load_avatar(rec["user_id"]) if rec.get("user_id") else None
            )
            if pic and exists.profile_picture != pic:
                exists.profile_picture = pic
                updated_pics += 1
            pp = exists.player_profile
            if pp:
                for fld in (
                    "address",
                    "emergency_contact",
                    "date_of_birth",
                    "batting_style",
                    "bowling_style",
                    "jersey_number",
                ):
                    if rec.get(fld) is not None and getattr(pp, fld) != rec.get(fld):
                        setattr(pp, fld, rec.get(fld))
                        updated_profiles += 1
                playing = role_map.get((rec.get("playing_role") or "").lower())
                if playing and pp.playing_role != playing:
                    pp.playing_role = playing
                    pp.is_wicketkeeper = playing == PlayingRole.wicketkeeper
                    updated_profiles += 1
            if not rec.get("user_id"):
                rec["user_id"] = exists.id
            continue

        user = User(
            username=username,
            email=email,
            full_name=rec.get("full_name") or username,
            phone=rec.get("phone"),
            password_hash=rec["password_hash"],
            account_status=AccountStatus.active,
        )
        if player_role:
            user.roles = [player_role]
        db.add(user)
        db.flush()

        # Prefer backup user_id mapping for avatar lookup; then new id
        pic = None
        if rec.get("user_id"):
            pic = load_avatar(rec["user_id"])
        if not pic:
            pic = load_avatar(user.id)
        if pic:
            user.profile_picture = pic
            updated_pics += 1

        # Persist mapping for future avatar saves
        rec["user_id"] = user.id

        team = None
        if rec.get("team_slug"):
            team = db.query(Team).filter(Team.slug == rec["team_slug"]).first()
        if not team:
            team = db.query(Team).filter(Team.slug == "senior-1st-xi").first()
        playing = role_map.get((rec.get("playing_role") or "").lower())
        count = db.query(PlayerProfile).count() + 1
        db.add(
            PlayerProfile(
                user_id=user.id,
                player_code=rec.get("player_code") or f"MCC-P-{count:04d}",
                team_id=team.id if team else None,
                address=rec.get("address"),
                jersey_number=rec.get("jersey_number"),
                emergency_contact=rec.get("emergency_contact"),
                date_of_birth=rec.get("date_of_birth"),
                batting_style=rec.get("batting_style"),
                bowling_style=rec.get("bowling_style"),
                playing_role=playing,
                is_wicketkeeper=playing == PlayingRole.wicketkeeper if playing else False,
                status=PlayerStatus.active,
            )
        )
        imported += 1

    if imported or updated_pics or updated_profiles:
        db.commit()
        print(
            f"github_user_store: restored {imported} users, "
            f"{updated_pics} avatars, {updated_profiles} profile fields"
        )
        # Write back user_id mappings
        try:
            save_users(users)
        except Exception as exc:  # noqa: BLE001
            print(f"user_id sync failed: {exc}")
    return imported


def restore_avatars_only(db) -> int:
    """Re-apply avatars from GitHub for all known users (even if already in DB)."""
    from app.models import User

    count = 0
    for user in db.query(User).all():
        pic = load_avatar(user.id)
        if pic and user.profile_picture != pic:
            user.profile_picture = pic
            count += 1
    # Also try by backup map
    for rec in load_users():
        uid = rec.get("user_id")
        email = (rec.get("email") or "").lower()
        if not uid:
            continue
        pic = load_avatar(uid)
        if not pic:
            continue
        user = db.query(User).filter(User.email == email).first() if email else db.get(User, uid)
        if user and (not user.profile_picture or user.profile_picture != pic):
            # If avatar file is under old id, also copy to current id path later
            user.profile_picture = pic
            count += 1
            if user.id != uid:
                save_avatar(user.id, pic)
    if count:
        db.commit()
        print(f"github_user_store: refreshed {count} avatars into DB")
    return count
