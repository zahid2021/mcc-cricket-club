from fastapi import APIRouter

from app.api.routes import auth, club, portal, players, admin

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(club.router)
api_router.include_router(portal.router)
api_router.include_router(players.router)
api_router.include_router(admin.router)
api_router.include_router(admin.public_router)
