from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["short"] == "MCC"


def test_login_admin():
    r = client.post(
        "/api/auth/login",
        json={"identifier": "admin", "password": "admin", "remember_me": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["primary_role"] == "super_admin"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_login_player_and_dashboard():
    r = client.post(
        "/api/auth/login",
        json={"identifier": "mali", "password": "Player@MCC2026"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    d = client.get(
        "/api/portal/player/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert d.status_code == 200
    body = d.json()
    assert body["welcome_name"] == "Muhammad Ali"
    assert "My Warnings" in body["sections"]


def test_rbac_blocks_player_from_needing_admin_perm():
    r = client.post(
        "/api/auth/login",
        json={"identifier": "mali", "password": "Player@MCC2026"},
    )
    token = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    perms = me.json()["permissions"]
    assert "finance.manage" not in perms
    assert "portal.player" in perms


def test_bad_login():
    r = client.post(
        "/api/auth/login",
        json={"identifier": "admin", "password": "wrong-password"},
    )
    assert r.status_code == 401
