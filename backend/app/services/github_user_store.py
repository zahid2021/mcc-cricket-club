"""Persist registered users to GitHub so Render free tier restarts don't wipe accounts."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import httpx

REPO = os.getenv("GITHUB_REPO", "zahid2021/mcc-cricket-club")
PATH = os.getenv("GITHUB_USERS_PATH", "data/registered_users.json")
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def _headers() -> dict[str, str]:
    if not TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def load_users() -> list[dict[str, Any]]:
    if not TOKEN:
        return []
    url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(url, headers=_headers())
            if r.status_code == 404:
                return []
            r.raise_for_status()
            data = r.json()
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
            users = json.loads(content or "[]")
            return users if isinstance(users, list) else []
    except Exception as exc:  # noqa: BLE001
        print(f"github_user_store load failed: {exc}")
        return []


def save_users(users: list[dict[str, Any]]) -> None:
    if not TOKEN:
        print("github_user_store: no GITHUB_TOKEN — skip persist")
        return
    url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
    body_content = json.dumps(users, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(body_content.encode("utf-8")).decode("ascii")
    sha = None
    try:
        with httpx.Client(timeout=20) as client:
            existing = client.get(url, headers=_headers())
            if existing.status_code == 200:
                sha = existing.json().get("sha")
            payload: dict[str, Any] = {
                "message": "chore: sync registered MCC users",
                "content": encoded,
                "branch": "main",
            }
            if sha:
                payload["sha"] = sha
            r = client.put(url, headers=_headers(), json=payload)
            if r.status_code not in (200, 201):
                print(f"github_user_store save failed: {r.status_code} {r.text[:300]}")
            else:
                print(f"github_user_store: saved {len(users)} users")
    except Exception as exc:  # noqa: BLE001
        print(f"github_user_store save error: {exc}")


def upsert_user(record: dict[str, Any]) -> None:
    users = load_users()
    email = (record.get("email") or "").lower()
    username = (record.get("username") or "").lower()
    replaced = False
    for i, u in enumerate(users):
        if u.get("email", "").lower() == email or u.get("username", "").lower() == username:
            users[i] = record
            replaced = True
            break
    if not replaced:
        users.append(record)
    save_users(users)


def restore_into_db(db) -> int:
    """Import backed-up users into SQLAlchemy DB if missing. Returns count imported."""
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
                playing_role=playing,
                is_wicketkeeper=playing == PlayingRole.wicketkeeper if playing else False,
                status=PlayerStatus.active,
            )
        )
        imported += 1
    if imported:
        db.commit()
        print(f"github_user_store: restored {imported} users into DB")
    return imported
