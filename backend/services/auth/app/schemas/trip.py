"""
Pydantic schemas for Trip Creation & Scheduling
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum


class TripStatusEnum(str, Enum):
    """Trip status enumeration"""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


# Route Schemas
class RouteCreateRequest(BaseModel):
    """Request schema for creating a new route"""

    route_code: str = Field(
        ..., min_length=2, max_length=20, description="Unique route code"
    )
    route_name: str = Field(..., min_length=3, max_length=255, description="Route name")
    origin_name: str = Field(
        ..., min_length=2, max_length=255, description="Origin location name"
    )
    destination_name: str = Field(
        ..., min_length=2, max_length=255, description="Destination location name"
    )
    distance_km: Optional[Decimal] = Field(
        None, ge=0, description="Route distance in kilometers"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None, ge=1, description="Estimated travel time in minutes"
    )
    base_fare: Decimal = Field(..., ge=0, description="Base fare for this route")
    waypoints: Optional[str] = Field(None, description="JSON string of route waypoints")
    description: Optional[str] = Field(
        None, max_length=500, description="Route description"
    )

    @field_validator("route_code")
    @classmethod
    def validate_route_code(cls, v):
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Route code must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.upper()


class RouteUpdateRequest(BaseModel):
    """Request schema for updating a route"""

    route_name: Optional[str] = Field(None, min_length=3, max_length=255)
    origin_name: Optional[str] = Field(None, min_length=2, max_length=255)
    destination_name: Optional[str] = Field(None, min_length=2, max_length=255)
    distance_km: Optional[Decimal] = Field(None, ge=0)
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    base_fare: Optional[Decimal] = Field(None, ge=0)
    waypoints: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = Field(None)


class RouteResponse(BaseModel):
    """Response schema for route data"""

    id: str
    fleet_id: str
    route_code: str
    route_name: str
    origin_name: str
    destination_name: str
    distance_km: Optional[float]
    estimated_duration_minutes: Optional[int]
    base_fare: float
    waypoints: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


# Trip Schemas
class TripCreateRequest(BaseModel):
    """Request schema for creating a new trip"""

    route_id: str = Field(..., description="Route ID for this trip")
    vehicle_id: str = Field(..., description="Vehicle ID assigned to this trip")
    driver_id: str = Field(..., description="Driver ID assigned to this trip")
    scheduled_departure: datetime = Field(
        ..., description="Scheduled departure datetime"
    )
    scheduled_arrival: Optional[datetime] = Field(
        None, description="Scheduled arrival datetime"
    )
    fare: Decimal = Field(..., ge=0, description="Trip fare amount")

    @field_validator("scheduled_arrival")
    @classmethod
    def validate_arrival_time(cls, v, info):
        if v and "scheduled_departure" in info.data:
            if v <= info.data["scheduled_departure"]:
                raise ValueError("Scheduled arrival must be after scheduled departure")
        return v

    @field_validator("scheduled_departure")
    @classmethod
    def validate_departure_time(cls, v):
        from datetime import timezone

        now = datetime.now(timezone.utc)
        # Make v timezone-aware if it's not already
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("Scheduled departure must be in the future")
        return v


class TripUpdateRequest(BaseModel):
    """Request schema for updating a trip"""

    vehicle_id: Optional[str] = Field(None, description="New vehicle ID")
    driver_id: Optional[str] = Field(None, description="New driver ID")
    scheduled_departure: Optional[datetime] = Field(
        None, description="New scheduled departure"
    )
    scheduled_arrival: Optional[datetime] = Field(
        None, description="New scheduled arrival"
    )
    fare: Optional[Decimal] = Field(None, ge=0, description="New fare amount")
    status: Optional[TripStatusEnum] = Field(None, description="Trip status")


class TripResponse(BaseModel):
    """Response schema for trip data"""

    id: str
    route_id: str
    vehicle_id: str
    driver_id: str
    scheduled_departure: str
    scheduled_arrival: Optional[str]
    actual_departure: Optional[str]
    actual_arrival: Optional[str]
    fare: float
    total_seats: int
    available_seats: int
    status: str
    created_at: str
    updated_at: str


class TripListResponse(BaseModel):
    """Response schema for trip list with pagination"""

    trips: List[TripResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


# Trip Template Schemas
class TripTemplateCreateRequest(BaseModel):
    """Request schema for creating a trip template"""

    template_name: str = Field(
        ..., min_length=3, max_length=255, description="Template name"
    )
    route_id: str = Field(..., description="Route ID for this template")
    departure_time: time = Field(..., description="Daily departure time")
    fare: Decimal = Field(..., ge=0, description="Template fare amount")
    days_of_week: List[int] = Field(
        ..., description="Days of week (1=Monday, 7=Sunday)"
    )

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v):
        if not v:
            raise ValueError("At least one day of week must be specified")
        for day in v:
            if day < 1 or day > 7:
                raise ValueError(
                    "Days of week must be between 1 (Monday) and 7 (Sunday)"
                )
        return sorted(list(set(v)))  # Remove duplicates and sort


class TripTemplateResponse(BaseModel):
    """Response schema for trip template data"""

    id: str
    route_id: str
    route_name: str
    fleet_id: str
    template_name: str
    departure_time: str
    fare: float
    days_of_week: List[int]
    is_active: bool
    created_by: str
    created_at: str
    updated_at: str


# Bulk Trip Creation
class BulkTripCreateRequest(BaseModel):
    """Request schema for bulk trip creation"""

    template_id: str = Field(..., description="Trip template ID")
    start_date: date = Field(..., description="Start date for trip generation")
    end_date: date = Field(..., description="End date for trip generation")
    vehicle_assignments: List[Dict[str, str]] = Field(
        ..., description="Vehicle and driver assignments"
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("vehicle_assignments")
    @classmethod
    def validate_assignments(cls, v):
        if not v:
            raise ValueError("At least one vehicle assignment must be provided")
        for assignment in v:
            if "vehicle_id" not in assignment or "driver_id" not in assignment:
                raise ValueError("Each assignment must have vehicle_id and driver_id")
        return v


class BulkTripCreateResponse(BaseModel):
    """Response schema for bulk trip creation"""

    success: bool
    message: str
    trips_created: int
    trip_ids: List[str]
    errors: List[str] = []


# Availability Check
class AvailabilityCheckRequest(BaseModel):
    """Request schema for checking vehicle/driver availability"""

    vehicle_id: Optional[str] = Field(None, description="Vehicle ID to check")
    driver_id: Optional[str] = Field(None, description="Driver ID to check")
    start_datetime: datetime = Field(..., description="Start of time period to check")
    end_datetime: datetime = Field(..., description="End of time period to check")

    @field_validator("end_datetime")
    @classmethod
    def validate_end_datetime(cls, v, info):
        if "start_datetime" in info.data and v <= info.data["start_datetime"]:
            raise ValueError("End datetime must be after start datetime")
        return v


class AvailabilityCheckResponse(BaseModel):
    """Response schema for availability check"""

    vehicle_id: Optional[str]
    driver_id: Optional[str]
    is_available: bool
    conflicting_trips: List[Dict[str, Any]] = []
    message: str


# Trip Statistics
class TripStatsResponse(BaseModel):
    """Response schema for trip statistics"""

    total_trips: int
    scheduled_trips: int
    active_trips: int
    completed_trips: int
    cancelled_trips: int
    total_revenue: float
    average_occupancy: float
    on_time_percentage: float
