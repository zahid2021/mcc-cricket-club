from fastapi import APIRouter

from app.api.routes import auth, club

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(club.router)
