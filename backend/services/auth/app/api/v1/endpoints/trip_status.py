"""
Trip Status Tracking API Endpoints
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager, get_current_user
from app.models.user_profile import UserProfile
from app.services.trip_status_service import TripStatusService
from app.schemas.trip_status import (
    TripStatusUpdateRequest,
    TripStatusUpdateResponse,
    TripStatusHistoryResponse,
    GPSLocationRequest,
    GPSLocationResponse,
    GPSLocationHistoryResponse,
    NotificationPreferenceRequest,
    NotificationPreferenceResponse,
    TripTrackingResponse,
    FleetTrackingResponse,
    DelayAlertRequest,
    DelayAlertResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/trips/{trip_id}/status",
    summary="Update trip status",
    description="Update the real-time status of a trip",
)
def update_trip_status(
    trip_id: UUID,
    request: TripStatusUpdateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Update trip status (Manager only)

    Args:
        trip_id: Trip UUID
        request: Status update request
        db: Database session
        manager: Current manager user

    Returns:
        Status update confirmation
    """
    try:
        success, response_data = TripStatusService.update_trip_status(
            trip_id=str(trip_id),
            request=request,
            updated_by=str(manager.id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "TRIP_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return {
            "success": True,
            "message": response_data["message"],
            "trip_id": response_data["trip_id"],
            "previous_status": response_data["previous_status"],
            "new_status": response_data["new_status"],
            "status_update": response_data["status_update"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status update failed",
        )


@router.get(
    "/trips/{trip_id}/status/history",
    response_model=TripStatusHistoryResponse,
    summary="Get trip status history",
    description="Get the status update history for a trip",
)
def get_trip_status_history(
    trip_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: UserProfile = Depends(get_current_user),
):
    """
    Get trip status history (Manager or Passenger)

    Args:
        trip_id: Trip UUID
        page: Page number
        limit: Items per page
        db: Database session
        user: Current user

    Returns:
        TripStatusHistoryResponse: Paginated status history
    """
    try:
        success, response_data = TripStatusService.get_trip_status_history(
            trip_id=str(trip_id),
            page=page,
            limit=limit,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "TRIP_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return TripStatusHistoryResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status history",
        )


@router.post(
    "/gps/locations",
    summary="Record GPS location",
    description="Record GPS location data for a vehicle",
)
def record_gps_location(
    request: GPSLocationRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Record GPS location (Manager only)

    Args:
        request: GPS location data
        db: Database session
        manager: Current manager user

    Returns:
        GPS location confirmation
    """
    try:
        success, response_data = TripStatusService.record_gps_location(
            request=request,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code in ["VEHICLE_NOT_FOUND", "TRIP_NOT_FOUND"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return {
            "success": True,
            "message": response_data["message"],
            "location": response_data["location"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS recording error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GPS location recording failed",
        )


@router.get(
    "/trips/{trip_id}/location",
    summary="Get current trip location",
    description="Get the current GPS location for a trip",
)
def get_current_trip_location(
    trip_id: UUID,
    db: Session = Depends(get_db),
    user: UserProfile = Depends(get_current_user),
):
    """
    Get current trip location (Manager or Passenger)

    Args:
        trip_id: Trip UUID
        db: Database session
        user: Current user

    Returns:
        Current GPS location
    """
    try:
        success, response_data = TripStatusService.get_current_trip_location(
            trip_id=str(trip_id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "TRIP_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code == "NO_LOCATION_DATA":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get location error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current location",
        )


@router.get(
    "/fleet/tracking",
    response_model=FleetTrackingResponse,
    summary="Fleet tracking dashboard",
    description="Get real-time tracking data for all fleet vehicles",
)
def get_fleet_tracking_dashboard(
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get fleet tracking dashboard (Manager only)

    Args:
        db: Database session
        manager: Current manager user

    Returns:
        FleetTrackingResponse: Fleet tracking data
    """
    try:
        success, response_data = TripStatusService.get_fleet_tracking_dashboard(
            fleet_id=str(manager.fleet_id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return FleetTrackingResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fleet tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get fleet tracking data",
        )


@router.post(
    "/trips/{trip_id}/delay-alert",
    response_model=DelayAlertResponse,
    summary="Create delay alert",
    description="Create a delay alert and notify passengers",
)
def create_delay_alert(
    trip_id: UUID,
    request: DelayAlertRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Create delay alert (Manager only)

    Args:
        trip_id: Trip UUID
        request: Delay alert request
        db: Database session
        manager: Current manager user

    Returns:
        DelayAlertResponse: Delay alert confirmation
    """
    try:
        # Set trip_id from URL parameter
        request.trip_id = str(trip_id)

        success, response_data = TripStatusService.create_delay_alert(
            request=request,
            manager_id=str(manager.id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "TRIP_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return DelayAlertResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delay alert error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create delay alert",
        )
