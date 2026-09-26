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


@app.middleware("http")
async def no_store_dynamic(request, call_next):
    """HTML pages + API must not be cached so homepage updates without hard refresh."""
    response = await call_next(request)
    path = request.url.path or ""
    if (
        path.startswith("/api/")
        or path in ("/", "/health")
        or path.startswith("/portal")
        or path in ("/login", "/signup", "/policy")
        or path.endswith(".html")
    ):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


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
                # leadership_role column (SQLite: add if missing)
                cols = [
                    r[1]
                    for r in conn.exec_driver_sql("PRAGMA table_info(player_profiles)").fetchall()
                ]
                if "leadership_role" not in cols:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN leadership_role VARCHAR(40) DEFAULT 'none'"
                    )
                if "discipline_type" not in cols:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN discipline_type VARCHAR(20)"
                    )
                if "discipline_reason" not in cols:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN discipline_reason VARCHAR(500)"
                    )
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
                try:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN IF NOT EXISTS leadership_role VARCHAR(40) DEFAULT 'none'"
                    )
                except Exception:  # noqa: BLE001
                    pass
                try:
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN IF NOT EXISTS discipline_type VARCHAR(20)"
                    )
                    conn.exec_driver_sql(
                        "ALTER TABLE player_profiles ADD COLUMN IF NOT EXISTS discipline_reason VARCHAR(500)"
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

        # Keep admin password simple as requested: admin / admin
        # (run after restore so GitHub backup cannot re-apply old hash)
        from app.models import User
        from app.core.security import hash_password, verify_password

        admin_user = (
            db.query(User)
            .filter((User.username == "admin") | (User.email == "admin@mustafacc.club"))
            .first()
        )
        if admin_user and not verify_password("admin", admin_user.password_hash):
            admin_user.password_hash = hash_password("admin")
            db.commit()
            print("admin password reset to: admin")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "club": "Mustafa Cricket Club", "short": "MCC"}


@app.get("/favicon.ico")
def favicon():
    path = STATIC_DIR / "favicon.ico"
    if path.exists():
        return FileResponse(path, media_type="image/x-icon")
    return {"error": "favicon not found"}


@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    path = STATIC_DIR / "images" / "mcc-apple-touch-icon.png"
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return {"error": "icon not found"}


def _page(name: str):
    path = STATIC_DIR / name
    if path.exists():
        # Avoid stale homepage/HTML after deploys
        return FileResponse(
            path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
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


@app.get("/portal")
def portal_gate_page():
    # Player Portal click → pehle login/signup gate (edit form nahi)
    return _page("portal-gate.html")


@app.get("/portal/player")
def player_portal_page():
    # Login ke baad: profile VIEW only
    return _page("portal-player.html")


@app.get("/portal/player/profile")
def player_profile_page():
    # Sirf Edit button se — Save ke baad wapas /portal/player
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
