"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, login, profile

api_router = APIRouter()

# Include auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(login.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profile.router, prefix="/auth", tags=["user-profile"])
