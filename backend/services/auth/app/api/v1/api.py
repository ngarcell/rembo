"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, login, profile, admin, manager

api_router = APIRouter()

# Include auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(login.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profile.router, prefix="/auth", tags=["user-profile"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(manager.router, prefix="/manager", tags=["manager"])
