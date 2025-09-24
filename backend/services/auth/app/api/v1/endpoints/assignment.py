"""
Assignment endpoints for managing driver-vehicle assignments
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager
from app.models.user_profile import UserProfile
from app.services.assignment_service import assignment_service
from app.schemas.assignment import (
    AssignmentRequest,
    CreateAssignmentResponse,
    AssignmentListResponse,
    UnassignRequest,
    UnassignResponse,
    AvailableDriversResponse,
    AvailableVehiclesResponse,
    AssignmentHistoryResponse,
    AssignmentResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/assignments",
    response_model=CreateAssignmentResponse,
    summary="Create driver-vehicle assignment",
    description="Assign a driver to a vehicle in the manager's fleet",
)
def create_assignment(
    request: AssignmentRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Create a new driver-vehicle assignment (Manager only)

    Args:
        request: Assignment request data
        db: Database session
        manager: Current manager user

    Returns:
        CreateAssignmentResponse: Assignment creation result
    """
    try:
        success, response_data = assignment_service.create_assignment(
            driver_id=request.driver_id,
            vehicle_id=request.vehicle_id,
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            assignment_notes=request.assignment_notes,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code in ["DRIVER_NOT_FOUND", "VEHICLE_NOT_FOUND"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code in ["DRIVER_ALREADY_ASSIGNED", "VEHICLE_ALREADY_ASSIGNED"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return CreateAssignmentResponse(
            success=True,
            message=response_data["message"],
            assignment=AssignmentResponse(**response_data["assignment"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assignment creation failed",
        )


@router.get(
    "/assignments",
    response_model=AssignmentListResponse,
    summary="List fleet assignments",
    description="Get list of driver-vehicle assignments in the manager's fleet",
)
def list_assignments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Show only active assignments"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    List assignments in manager's fleet

    Args:
        page: Page number (1-based)
        limit: Items per page
        active_only: Filter for active assignments only
        db: Database session
        manager: Current manager user

    Returns:
        AssignmentListResponse: List of assignments with pagination
    """
    try:
        success, response_data = assignment_service.get_fleet_assignments(
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            page=page,
            limit=limit,
            active_only=active_only,
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return AssignmentListResponse(
            assignments=[
                AssignmentResponse(**assignment)
                for assignment in response_data["assignments"]
            ],
            total_count=response_data["total_count"],
            page=response_data["page"],
            limit=response_data["limit"],
            total_pages=response_data["total_pages"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List assignments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assignments",
        )


@router.delete(
    "/assignments/{assignment_id}",
    response_model=UnassignResponse,
    summary="Unassign driver from vehicle",
    description="Remove driver-vehicle assignment",
)
def unassign_driver(
    assignment_id: UUID,
    request: UnassignRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Unassign driver from vehicle (Manager only)

    Args:
        assignment_id: Assignment UUID
        request: Unassignment request with optional notes
        db: Database session
        manager: Current manager user

    Returns:
        UnassignResponse: Unassignment result
    """
    try:
        success, response_data = assignment_service.unassign_driver(
            assignment_id=str(assignment_id),
            manager_id=str(manager.id),
            notes=request.notes,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "ASSIGNMENT_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return UnassignResponse(
            success=True,
            message=response_data["message"],
            assignment_id=response_data["assignment_id"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unassignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unassignment failed",
        )


@router.get(
    "/assignments/available-drivers",
    response_model=AvailableDriversResponse,
    summary="Get available drivers",
    description="Get list of drivers available for assignment",
)
def get_available_drivers(
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get drivers available for assignment

    Args:
        db: Database session
        manager: Current manager user

    Returns:
        AvailableDriversResponse: List of available drivers
    """
    try:
        success, response_data = assignment_service.get_available_drivers(
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return AvailableDriversResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get available drivers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available drivers",
        )


@router.get(
    "/assignments/available-vehicles",
    response_model=AvailableVehiclesResponse,
    summary="Get available vehicles",
    description="Get list of vehicles available for assignment",
)
def get_available_vehicles(
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get vehicles available for assignment

    Args:
        db: Database session
        manager: Current manager user

    Returns:
        AvailableVehiclesResponse: List of available vehicles
    """
    try:
        success, response_data = assignment_service.get_available_vehicles(
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return AvailableVehiclesResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get available vehicles error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available vehicles",
        )


@router.get(
    "/assignments/history",
    response_model=AssignmentHistoryResponse,
    summary="Get assignment history",
    description="Get historical assignment data including inactive assignments",
)
def get_assignment_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get assignment history including inactive assignments

    Args:
        page: Page number (1-based)
        limit: Items per page
        db: Database session
        manager: Current manager user

    Returns:
        AssignmentHistoryResponse: Historical assignment data
    """
    try:
        success, response_data = assignment_service.get_fleet_assignments(
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            page=page,
            limit=limit,
            active_only=False,  # Include inactive assignments for history
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return AssignmentHistoryResponse(
            assignments=[
                AssignmentResponse(**assignment)
                for assignment in response_data["assignments"]
            ],
            total_count=response_data["total_count"],
            page=response_data["page"],
            limit=response_data["limit"],
            total_pages=response_data["total_pages"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get assignment history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assignment history",
        )
