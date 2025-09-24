"""
Assignment schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AssignmentRequest(BaseModel):
    """Request schema for creating driver-vehicle assignment"""

    driver_id: str = Field(..., description="Driver UUID")
    vehicle_id: str = Field(..., description="Vehicle UUID")
    assignment_notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the assignment"
    )


class AssignmentResponse(BaseModel):
    """Response schema for assignment information"""

    id: str
    driver_id: str
    vehicle_id: str
    driver_name: str
    vehicle_info: str  # "KCS-001 (KCA123A)"
    assigned_at: str
    unassigned_at: Optional[str] = None
    is_active: bool
    assignment_notes: Optional[str] = None
    created_at: str


class CreateAssignmentResponse(BaseModel):
    """Response schema for assignment creation"""

    success: bool
    message: str
    assignment: AssignmentResponse


class AssignmentListResponse(BaseModel):
    """Response schema for assignment list"""

    assignments: List[AssignmentResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class UnassignRequest(BaseModel):
    """Request schema for unassigning driver"""

    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the unassignment"
    )


class UnassignResponse(BaseModel):
    """Response schema for unassignment"""

    success: bool
    message: str
    assignment_id: str


class AvailableDriver(BaseModel):
    """Schema for available driver information"""

    id: str
    driver_id: str
    name: str
    phone: str
    license_number: str


class AvailableDriversResponse(BaseModel):
    """Response schema for available drivers"""

    available_drivers: List[AvailableDriver]
    count: int


class AvailableVehicle(BaseModel):
    """Schema for available vehicle information"""

    id: str
    fleet_number: str
    license_plate: str
    capacity: int
    status: str


class AvailableVehiclesResponse(BaseModel):
    """Response schema for available vehicles"""

    available_vehicles: List[AvailableVehicle]
    count: int


class AssignmentHistoryResponse(BaseModel):
    """Response schema for assignment history"""

    assignments: List[AssignmentResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class AssignmentSummary(BaseModel):
    """Schema for assignment summary statistics"""

    total_assignments: int
    active_assignments: int
    available_drivers: int
    available_vehicles: int
    assignment_rate: float  # percentage of drivers assigned


class FleetAssignmentSummaryResponse(BaseModel):
    """Response schema for fleet assignment summary"""

    summary: AssignmentSummary
