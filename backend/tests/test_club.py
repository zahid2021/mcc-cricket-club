from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_public_club():
    r = client.get("/api/club")
    assert r.status_code == 200
    assert r.json()["short_name"] == "MCC"


def test_teams_seeded():
    r = client.get("/api/teams")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "Senior 1st XI" in names
    assert "U16" in names
