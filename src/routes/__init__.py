from fastapi import APIRouter

from src.routes import login, notes, ping, users

api_router = APIRouter()
api_router.include_router(ping.router)
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
