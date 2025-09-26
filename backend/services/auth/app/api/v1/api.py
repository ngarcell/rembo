"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    login,
    profile,
    admin,
    assignment,
    manager,
    vehicle,
    vehicle_status,
    fleet_analytics,
    trip,
    trip_status,
    booking,
    payments,
)

api_router = APIRouter()

# Include auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(login.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profile.router, prefix="/auth", tags=["user-profile"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(assignment.router, prefix="/manager", tags=["assignments"])
api_router.include_router(manager.router, prefix="/manager", tags=["manager"])
api_router.include_router(vehicle.router, prefix="/manager", tags=["manager"])
api_router.include_router(
    vehicle_status.router, prefix="/manager", tags=["vehicle-status"]
)
api_router.include_router(
    fleet_analytics.router, prefix="/manager/analytics", tags=["fleet-analytics"]
)
api_router.include_router(
    trip.router, prefix="/manager/trips", tags=["trip-management"]
)
api_router.include_router(trip_status.router, prefix="/manager", tags=["trip-status"])
api_router.include_router(booking.router, prefix="/passenger", tags=["booking-system"])
api_router.include_router(payments.router, prefix="/payments", tags=["payment-processing"])
