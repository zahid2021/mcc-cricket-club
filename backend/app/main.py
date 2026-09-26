"""Mustafa Cricket Club — Management & Operations API."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.router import api_router
from app.db.session import engine
from app.db.base import Base

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="MCC Cricket Club API",
    description="Mustafa Cricket Club — Management & Operations Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    # Ensure profile_picture can hold full base64 images (old DBs used VARCHAR(500))
    try:
        with engine.begin() as conn:
            dialect = engine.dialect.name
            if dialect == "sqlite":
                # SQLite ignores VARCHAR length, but recreate affinity via no-op is fine
                conn.exec_driver_sql(
                    "CREATE TABLE IF NOT EXISTS _mcc_migrate_note (id INTEGER)"
                )
                # Allow same jersey on a team (was blocking Save with 500)
                conn.exec_driver_sql("DROP INDEX IF EXISTS uq_jersey_team")
            elif dialect.startswith("postgres"):
                conn.exec_driver_sql(
                    "ALTER TABLE users ALTER COLUMN profile_picture TYPE TEXT"
                )
                conn.exec_driver_sql("DROP INDEX IF EXISTS uq_jersey_team")
                try:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles DROP CONSTRAINT IF EXISTS uq_jersey_team"
                    )
                except Exception:  # noqa: BLE001
                    pass
    except Exception as exc:  # noqa: BLE001
        print(f"profile_picture migrate note: {exc}")

    from app.db.seed import seed_if_empty
    from app.db.session import SessionLocal
    from app.services.github_user_store import restore_into_db, restore_avatars_only

    seed_if_empty()
    db = SessionLocal()
    try:
        restore_into_db(db)
        restore_avatars_only(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "club": "Mustafa Cricket Club", "short": "MCC"}


def _page(name: str):
    path = STATIC_DIR / name
    if path.exists():
        return FileResponse(path)
    return {"error": "page not found"}


@app.get("/")
def public_home():
    return _page("index.html")


@app.get("/login")
def login_page():
    return _page("login.html")


@app.get("/signup")
def signup_page():
    return _page("signup.html")


@app.get("/policy")
def policy_page():
    return _page("policy.html")


@app.get("/portal/player")
def player_portal_page():
    # Player portal = My Profile (full editable form)
    return _page("portal-profile.html")


@app.get("/portal/player/profile")
def player_profile_page():
    return _page("portal-profile.html")


@app.get("/portal/player/notifications")
def player_notifications_page():
    return _page("portal-notifications.html")


@app.get("/portal/player/warnings")
def player_warnings_page():
    return _page("portal-notifications.html")


@app.get("/portal/player/team")
def player_team_page():
    return _page("portal-team.html")


@app.get("/portal/player/section")
def player_section_page():
    return _page("portal-section.html")


@app.get("/portal/staff-tools")
def staff_tools_page():
    return _page("portal-staff-tools.html")


@app.get("/portal/admin")
def admin_portal_page():
    return _page("portal-admin.html")


@app.get("/portal/staff")
def staff_portal_page():
    # Staff uses player-style portal for now
    return _page("portal-player.html")
