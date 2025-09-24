"""
Trip Management API Endpoints
"""

import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager
from app.models.user_profile import UserProfile
from app.services.trip_service import TripService
from app.schemas.trip import (
    RouteCreateRequest,
    RouteUpdateRequest,
    RouteResponse,
    TripCreateRequest,
    TripUpdateRequest,
    TripResponse,
    TripListResponse,
    TripTemplateCreateRequest,
    TripTemplateResponse,
    BulkTripCreateRequest,
    BulkTripCreateResponse,
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
    TripStatsResponse,
    TripStatusEnum,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Route Management Endpoints
@router.post("/routes", response_model=dict)
def create_route(
    request: RouteCreateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Create a new route"""
    try:
        success, result = TripService.create_route(
            fleet_id=manager.fleet_id,
            request=request,
            manager_id=str(manager.id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create route"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_route endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/routes")
def get_routes(
    active_only: bool = Query(True, description="Filter for active routes only"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get all routes for the manager's fleet"""
    try:
        success, result = TripService.get_routes(
            fleet_id=manager.fleet_id, db=db, active_only=active_only
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retrieve routes"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_routes endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/routes/{route_id}")
def update_route(
    route_id: str,
    request: RouteUpdateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Update an existing route"""
    try:
        success, result = TripService.update_route(
            route_id=route_id, fleet_id=manager.fleet_id, request=request, db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to update route"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_route endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Trip Management Endpoints
@router.post("/trips")
def create_trip(
    request: TripCreateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Create a new trip"""
    try:
        success, result = TripService.create_trip(
            fleet_id=manager.fleet_id,
            request=request,
            manager_id=str(manager.id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create trip"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_trip endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/trips")
def get_trips(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[TripStatusEnum] = Query(None, description="Filter by trip status"),
    route_id: Optional[str] = Query(None, description="Filter by route ID"),
    start_date: Optional[date] = Query(None, description="Filter trips from this date"),
    end_date: Optional[date] = Query(None, description="Filter trips until this date"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get trips with filtering and pagination"""
    try:
        success, result = TripService.get_trips(
            fleet_id=manager.fleet_id,
            db=db,
            page=page,
            limit=limit,
            status=status.value if status else None,
            route_id=route_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retrieve trips"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_trips endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/trips/{trip_id}")
def update_trip(
    trip_id: str,
    request: TripUpdateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Update an existing trip"""
    try:
        success, result = TripService.update_trip(
            trip_id=trip_id,
            fleet_id=manager.fleet_id,
            request=request,
            manager_id=str(manager.id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to update trip"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_trip endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/trips/{trip_id}")
def cancel_trip(
    trip_id: str,
    cancellation_reason: str = Query(..., description="Reason for cancellation"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Cancel a trip"""
    try:
        success, result = TripService.cancel_trip(
            trip_id=trip_id,
            fleet_id=manager.fleet_id,
            cancellation_reason=cancellation_reason,
            manager_id=str(manager.id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to cancel trip"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cancel_trip endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Availability Check Endpoint
@router.post("/availability/check")
def check_availability(
    request: AvailabilityCheckRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Check vehicle and driver availability"""
    try:
        success, result = TripService.check_availability(
            fleet_id=manager.fleet_id, request=request, db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to check availability"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_availability endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
