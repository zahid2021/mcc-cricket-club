# Mustafa Cricket Club (MCC) — Management & Operations Platform

Professional cricket club management system for **Mustafa Cricket Club**.

## Stack

| Layer | Tech |
|--------|------|
| Public site + portals | Next.js 15, TypeScript, Tailwind CSS |
| API | FastAPI, SQLAlchemy, Pydantic, JWT |
| Database | SQLite (dev) / PostgreSQL (Docker) |

## Quick start (local)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Site: http://localhost:3000

### Seeded logins

| User | Password | Role |
|------|----------|------|
| `admin` | `Admin@MCC2026` | Super Admin |
| `mali` | `Player@MCC2026` | Player (Muhammad Ali) |
| `captain` | `Captain@MCC2026` | Captain |

## Brand

- Motto: *Play Hard. Stay Humble. Win Together.*
- Tagline: *One Team. One Dream.*
- Hero: full-bleed MCC poster (`frontend/public/images/mcc-hero.png`)

## Phases

Phase 1 (done): foundation, auth, RBAC, public site + hero, player/admin shells, seed data.

Remaining: matches/selection, live scoring, discipline, finance, reports (see product PRD).
