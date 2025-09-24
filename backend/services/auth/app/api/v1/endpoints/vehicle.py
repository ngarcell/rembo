"""
Vehicle management endpoints for managers
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user_profile import UserProfile
from app.services.vehicle_service import VehicleService
from app.schemas.vehicle import (
    VehicleRegistrationRequest,
    VehicleRegistrationResponse,
    VehicleListResponse,
    VehicleDetailsResponse,
    VehicleUpdateRequest,
    VehicleResponse,
    VehicleSummaryResponse
)

router = APIRouter()


@router.post("/vehicles", response_model=VehicleRegistrationResponse)
async def register_vehicle(
    vehicle_data: VehicleRegistrationRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new vehicle in the manager's fleet
    
    Requires manager role and valid fleet assignment.
    """
    # Verify user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can register vehicles")
    
    if not current_user.fleet_id:
        raise HTTPException(status_code=400, detail="Manager must be assigned to a fleet")
    
    # Register vehicle
    success, vehicle, error = VehicleService.register_vehicle(
        vehicle_data=vehicle_data,
        manager_id=str(current_user.id),
        fleet_id=str(current_user.fleet_id),
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    # Get fleet name
    fleet_name = VehicleService.get_fleet_name(str(current_user.fleet_id), db)
    
    return VehicleRegistrationResponse(
        success=True,
        message="Vehicle registered successfully",
        vehicle=VehicleResponse(**vehicle.to_dict())
    )


@router.get("/vehicles", response_model=VehicleListResponse)
async def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of vehicles in the manager's fleet
    
    Supports pagination, search, and filtering.
    """
    # Verify user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view vehicles")
    
    if not current_user.fleet_id:
        raise HTTPException(status_code=400, detail="Manager must be assigned to a fleet")
    
    # Get vehicles
    vehicles, total_count = VehicleService.get_fleet_vehicles(
        fleet_id=str(current_user.fleet_id),
        manager_id=str(current_user.id),
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status,
        vehicle_type=vehicle_type
    )
    
    # Convert to response format
    vehicle_summaries = [
        VehicleSummaryResponse(**vehicle.to_summary_dict())
        for vehicle in vehicles
    ]
    
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    
    return VehicleListResponse(
        vehicles=vehicle_summaries,
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/vehicles/{vehicle_id}", response_model=VehicleDetailsResponse)
async def get_vehicle_details(
    vehicle_id: str,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific vehicle
    
    Manager can only access vehicles in their fleet.
    """
    # Verify user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view vehicle details")
    
    # Get vehicle
    vehicle = VehicleService.get_vehicle_by_id(
        vehicle_id=vehicle_id,
        manager_id=str(current_user.id),
        db=db
    )
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Get fleet name
    fleet_name = VehicleService.get_fleet_name(str(vehicle.fleet_id), db)
    
    return VehicleDetailsResponse(
        success=True,
        vehicle=VehicleResponse(**vehicle.to_dict()),
        fleet_name=fleet_name
    )


@router.put("/vehicles/{vehicle_id}", response_model=VehicleDetailsResponse)
async def update_vehicle(
    vehicle_id: str,
    vehicle_data: VehicleUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update vehicle information
    
    Manager can only update vehicles in their fleet.
    """
    # Verify user is a manager
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can update vehicles")
    
    # Update vehicle
    success, vehicle, error = VehicleService.update_vehicle(
        vehicle_id=vehicle_id,
        vehicle_data=vehicle_data,
        manager_id=str(current_user.id),
        db=db
    )
    
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    
    # Get fleet name
    fleet_name = VehicleService.get_fleet_name(str(vehicle.fleet_id), db)
    
    return VehicleDetailsResponse(
        success=True,
        vehicle=VehicleResponse(**vehicle.to_dict()),
        fleet_name=fleet_name
    )
