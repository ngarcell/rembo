"""
Pydantic schemas for vehicle status and maintenance tracking
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class VehicleStatusEnum(str, Enum):
    """Vehicle operational status"""

    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    INSPECTION = "inspection"
    REPAIR = "repair"
    RETIRED = "retired"


class MaintenanceTypeEnum(str, Enum):
    """Types of maintenance"""

    ROUTINE = "routine"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"


class MaintenancePriorityEnum(str, Enum):
    """Maintenance priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Status History Schemas
class StatusChangeRequest(BaseModel):
    """Request to change vehicle status"""

    new_status: VehicleStatusEnum = Field(..., description="New vehicle status")
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for status change"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class StatusHistoryResponse(BaseModel):
    """Vehicle status history entry"""

    id: str
    vehicle_id: str
    previous_status: Optional[VehicleStatusEnum]
    new_status: VehicleStatusEnum
    changed_by: str
    changed_by_name: Optional[str] = None
    reason: Optional[str]
    notes: Optional[str]
    changed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Maintenance Schemas
class MaintenanceRecordRequest(BaseModel):
    """Request to create maintenance record"""

    maintenance_type: MaintenanceTypeEnum = Field(
        ..., description="Type of maintenance"
    )
    priority: MaintenancePriorityEnum = Field(
        MaintenancePriorityEnum.MEDIUM, description="Priority level"
    )
    title: str = Field(
        ..., min_length=1, max_length=200, description="Maintenance title"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Detailed description"
    )
    scheduled_date: Optional[datetime] = Field(
        None, description="Scheduled maintenance date"
    )
    assigned_to: Optional[str] = Field(
        None, max_length=200, description="Assigned mechanic/provider"
    )
    estimated_cost: Optional[int] = Field(
        None, ge=0, description="Estimated cost in cents"
    )
    odometer_reading: Optional[int] = Field(
        None, ge=0, description="Current odometer reading in km"
    )


class MaintenanceRecordUpdate(BaseModel):
    """Update maintenance record"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, max_length=200)
    performed_by: Optional[str] = Field(None, max_length=200)
    actual_cost: Optional[int] = Field(None, ge=0, description="Actual cost in cents")
    is_completed: Optional[bool] = None
    is_approved: Optional[bool] = None
    odometer_reading: Optional[int] = Field(None, ge=0)
    next_service_km: Optional[int] = Field(None, ge=0)
    next_service_date: Optional[datetime] = None


class MaintenanceRecordResponse(BaseModel):
    """Maintenance record response"""

    id: str
    vehicle_id: str
    vehicle_info: Optional[str] = None  # "Fleet-001 (KCA123A)"
    maintenance_type: MaintenanceTypeEnum
    priority: MaintenancePriorityEnum
    title: str
    description: Optional[str]
    scheduled_date: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    assigned_to: Optional[str]
    performed_by: Optional[str]
    created_by: str
    estimated_cost: Optional[int]
    actual_cost: Optional[int]
    is_completed: bool
    is_approved: bool
    odometer_reading: Optional[int]
    next_service_km: Optional[int]
    next_service_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class VehicleDocumentRequest(BaseModel):
    """Request to add vehicle document"""

    document_type: str = Field(
        ..., min_length=1, max_length=100, description="Type of document"
    )
    document_number: Optional[str] = Field(
        None, max_length=100, description="Document number"
    )
    issuer: Optional[str] = Field(None, max_length=200, description="Document issuer")
    issued_date: Optional[date] = Field(None, description="Date document was issued")
    expiry_date: Optional[date] = Field(None, description="Document expiry date")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class VehicleDocumentResponse(BaseModel):
    """Vehicle document response"""

    id: str
    vehicle_id: str
    document_type: str
    document_number: Optional[str]
    issuer: Optional[str]
    issued_date: Optional[date]
    expiry_date: Optional[date]
    is_active: bool
    is_expired: bool
    file_path: Optional[str]
    file_name: Optional[str]
    notes: Optional[str]
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Inspection Schemas
class VehicleInspectionRequest(BaseModel):
    """Request to add vehicle inspection"""

    inspection_type: str = Field(
        ..., min_length=1, max_length=100, description="Type of inspection"
    )
    inspector_name: Optional[str] = Field(
        None, max_length=200, description="Inspector name"
    )
    inspection_station: Optional[str] = Field(
        None, max_length=200, description="Inspection station"
    )
    inspection_date: datetime = Field(..., description="Date of inspection")
    passed: Optional[bool] = Field(None, description="Did vehicle pass inspection")
    score: Optional[int] = Field(
        None, ge=0, le=100, description="Inspection score if applicable"
    )
    findings: Optional[str] = Field(
        None, max_length=2000, description="Inspection findings"
    )
    recommendations: Optional[str] = Field(
        None, max_length=2000, description="Recommendations"
    )
    certificate_number: Optional[str] = Field(
        None, max_length=100, description="Certificate number"
    )
    next_inspection_date: Optional[datetime] = Field(
        None, description="Next inspection due date"
    )
    odometer_reading: Optional[int] = Field(
        None, ge=0, description="Odometer reading at inspection"
    )


class VehicleInspectionResponse(BaseModel):
    """Vehicle inspection response"""

    id: str
    vehicle_id: str
    vehicle_info: Optional[str] = None
    inspection_type: str
    inspector_name: Optional[str]
    inspection_station: Optional[str]
    passed: Optional[bool]
    score: Optional[int]
    inspection_date: datetime
    next_inspection_date: Optional[datetime]
    findings: Optional[str]
    recommendations: Optional[str]
    certificate_number: Optional[str]
    odometer_reading: Optional[int]
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List Response Schemas
class MaintenanceListResponse(BaseModel):
    """Paginated maintenance records response"""

    maintenance_records: List[MaintenanceRecordResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class StatusHistoryListResponse(BaseModel):
    """Paginated status history response"""

    status_history: List[StatusHistoryResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class DocumentListResponse(BaseModel):
    """Paginated documents response"""

    documents: List[VehicleDocumentResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class InspectionListResponse(BaseModel):
    """Paginated inspections response"""

    inspections: List[VehicleInspectionResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


# Dashboard/Summary Schemas
class VehicleStatusSummary(BaseModel):
    """Vehicle status summary for dashboard"""

    vehicle_id: str
    fleet_number: str
    license_plate: str
    current_status: VehicleStatusEnum
    last_maintenance: Optional[datetime]
    next_maintenance: Optional[datetime]
    last_inspection: Optional[datetime]
    next_inspection: Optional[datetime]
    pending_maintenance_count: int
    overdue_maintenance_count: int
    compliance_issues: List[str]


class FleetStatusDashboard(BaseModel):
    """Fleet status dashboard summary"""

    total_vehicles: int
    active_vehicles: int
    maintenance_vehicles: int
    out_of_service_vehicles: int
    pending_maintenance: int
    overdue_maintenance: int
    upcoming_inspections: int
    overdue_inspections: int
    compliance_issues: int
    vehicles: List[VehicleStatusSummary]
