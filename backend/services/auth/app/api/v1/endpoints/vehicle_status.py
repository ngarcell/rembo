"""
Vehicle status and maintenance tracking endpoints
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager
from app.models.user_profile import UserProfile
from app.services.vehicle_status_service import vehicle_status_service
from app.schemas.vehicle_status import (
    StatusChangeRequest,
    StatusHistoryListResponse,
    MaintenanceRecordRequest,
    MaintenanceRecordResponse,
    MaintenanceListResponse,
    VehicleStatusEnum,
    MaintenancePriorityEnum,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/vehicles/{vehicle_id}/status",
    summary="Change vehicle status",
    description="Change the operational status of a vehicle and record the change",
)
def change_vehicle_status(
    vehicle_id: UUID,
    request: StatusChangeRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Change vehicle status (Manager only)

    Args:
        vehicle_id: Vehicle UUID
        request: Status change request
        db: Database session
        manager: Current manager user

    Returns:
        Status change confirmation
    """
    try:
        success, response_data = vehicle_status_service.change_vehicle_status(
            vehicle_id=str(vehicle_id),
            new_status=request.new_status,
            manager_id=str(manager.id),
            reason=request.reason,
            notes=request.notes,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "VEHICLE_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code == "ACCESS_DENIED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
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
            "vehicle_id": response_data["vehicle_id"],
            "previous_status": response_data["previous_status"],
            "new_status": response_data["new_status"],
            "changed_at": response_data["changed_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status change failed",
        )


@router.get(
    "/vehicles/{vehicle_id}/status/history",
    response_model=StatusHistoryListResponse,
    summary="Get vehicle status history",
    description="Get the status change history for a vehicle",
)
def get_vehicle_status_history(
    vehicle_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get vehicle status history

    Args:
        vehicle_id: Vehicle UUID
        page: Page number (1-based)
        limit: Items per page
        db: Database session
        manager: Current manager user

    Returns:
        StatusHistoryListResponse: Paginated status history
    """
    try:
        success, response_data = vehicle_status_service.get_vehicle_status_history(
            vehicle_id=str(vehicle_id),
            manager_id=str(manager.id),
            page=page,
            limit=limit,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "VEHICLE_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code == "ACCESS_DENIED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return StatusHistoryListResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get status history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status history",
        )


@router.post(
    "/vehicles/{vehicle_id}/maintenance",
    response_model=dict,
    summary="Create maintenance record",
    description="Create a new maintenance record for a vehicle",
)
def create_maintenance_record(
    vehicle_id: UUID,
    request: MaintenanceRecordRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Create maintenance record (Manager only)

    Args:
        vehicle_id: Vehicle UUID
        request: Maintenance record request
        db: Database session
        manager: Current manager user

    Returns:
        Maintenance record creation result
    """
    try:
        # Convert request to dict
        maintenance_data = {
            "maintenance_type": request.maintenance_type,
            "priority": request.priority,
            "title": request.title,
            "description": request.description,
            "scheduled_date": request.scheduled_date,
            "assigned_to": request.assigned_to,
            "estimated_cost": request.estimated_cost,
            "odometer_reading": request.odometer_reading,
        }

        success, response_data = vehicle_status_service.create_maintenance_record(
            vehicle_id=str(vehicle_id),
            manager_id=str(manager.id),
            maintenance_data=maintenance_data,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "VEHICLE_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code == "ACCESS_DENIED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
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
            "maintenance_record": response_data["maintenance_record"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create maintenance record error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Maintenance record creation failed",
        )


@router.get(
    "/maintenance",
    response_model=MaintenanceListResponse,
    summary="List fleet maintenance records",
    description="Get maintenance records for the manager's fleet with filtering options",
)
def list_maintenance_records(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(
        None, description="Filter by status: pending, completed"
    ),
    priority_filter: Optional[MaintenancePriorityEnum] = Query(
        None, description="Filter by priority"
    ),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    List maintenance records for fleet

    Args:
        page: Page number (1-based)
        limit: Items per page
        status_filter: Filter by completion status
        priority_filter: Filter by priority level
        db: Database session
        manager: Current manager user

    Returns:
        MaintenanceListResponse: Paginated maintenance records
    """
    try:
        success, response_data = vehicle_status_service.get_fleet_maintenance_records(
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            page=page,
            limit=limit,
            status_filter=status_filter,
            priority_filter=priority_filter.value if priority_filter else None,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "ACCESS_DENIED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return MaintenanceListResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List maintenance records error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve maintenance records",
        )
