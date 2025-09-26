"""
Pydantic schemas for Trip Status Tracking
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TripStatusEnum(str, Enum):
    """Trip status enumeration for real-time tracking"""

    SCHEDULED = "scheduled"
    DEPARTED = "departed"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class UpdateSourceEnum(str, Enum):
    """Source of status update"""

    SYSTEM = "system"
    DRIVER = "driver"
    GPS = "gps"
    MANUAL = "manual"
    PASSENGER = "passenger"


class TripStatusUpdateRequest(BaseModel):
    """Request to update trip status"""

    status: TripStatusEnum
    location_lat: Optional[Decimal] = Field(None, description="Latitude coordinate")
    location_lng: Optional[Decimal] = Field(None, description="Longitude coordinate")
    location_name: Optional[str] = Field(
        None, max_length=255, description="Location name"
    )
    estimated_arrival: Optional[datetime] = Field(
        None, description="Updated estimated arrival time"
    )
    delay_minutes: Optional[int] = Field(0, ge=0, description="Delay in minutes")
    update_source: UpdateSourceEnum = Field(
        UpdateSourceEnum.MANUAL, description="Source of update"
    )
    notes: Optional[str] = Field(None, description="Additional notes")


class TripStatusUpdateResponse(BaseModel):
    """Response for trip status update"""

    id: str
    trip_id: str
    status: TripStatusEnum
    location_lat: Optional[Decimal]
    location_lng: Optional[Decimal]
    location_name: Optional[str]
    estimated_arrival: Optional[datetime]
    delay_minutes: int
    update_source: UpdateSourceEnum
    notes: Optional[str]
    updated_by: Optional[str]
    created_at: datetime


class TripStatusHistoryResponse(BaseModel):
    """Response for trip status history"""

    status_updates: List[TripStatusUpdateResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class GPSLocationRequest(BaseModel):
    """Request to record GPS location"""

    vehicle_id: str
    trip_id: Optional[str] = None
    latitude: Decimal = Field(..., description="Latitude coordinate")
    longitude: Decimal = Field(..., description="Longitude coordinate")
    altitude: Optional[Decimal] = Field(None, description="Altitude in meters")
    speed_kmh: Optional[Decimal] = Field(None, ge=0, description="Speed in km/h")
    heading: Optional[Decimal] = Field(
        None, ge=0, le=360, description="Compass heading 0-360"
    )
    accuracy_meters: Optional[int] = Field(
        None, ge=0, description="GPS accuracy in meters"
    )
    recorded_at: datetime = Field(..., description="When GPS reading was taken")


class GPSLocationResponse(BaseModel):
    """Response for GPS location"""

    id: str
    vehicle_id: str
    trip_id: Optional[str]
    latitude: Decimal
    longitude: Decimal
    altitude: Optional[Decimal]
    speed_kmh: Optional[Decimal]
    heading: Optional[Decimal]
    accuracy_meters: Optional[int]
    recorded_at: datetime
    received_at: datetime


class GPSLocationHistoryResponse(BaseModel):
    """Response for GPS location history"""

    locations: List[GPSLocationResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class NotificationPreferenceRequest(BaseModel):
    """Request to update notification preferences"""

    sms_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    trip_status_updates: Optional[bool] = None
    delay_notifications: Optional[bool] = None
    cancellation_alerts: Optional[bool] = None
    booking_confirmations: Optional[bool] = None
    advance_notice_minutes: Optional[int] = Field(None, ge=0, le=1440)


class NotificationPreferenceResponse(BaseModel):
    """Response for notification preferences"""

    id: str
    user_id: str
    sms_enabled: bool
    email_enabled: bool
    push_enabled: bool
    trip_status_updates: bool
    delay_notifications: bool
    cancellation_alerts: bool
    booking_confirmations: bool
    advance_notice_minutes: int
    created_at: datetime
    updated_at: datetime


class TripTrackingResponse(BaseModel):
    """Response for real-time trip tracking"""

    trip_id: str
    trip_code: str
    current_status: TripStatusEnum
    scheduled_departure: datetime
    scheduled_arrival: Optional[datetime]
    actual_departure: Optional[datetime]
    estimated_arrival: Optional[datetime]
    delay_minutes: int

    # Current location
    current_location: Optional[GPSLocationResponse]

    # Route information
    route_name: str
    origin_name: str
    destination_name: str

    # Vehicle and driver info
    vehicle_info: str
    driver_name: str

    # Recent status updates
    recent_updates: List[TripStatusUpdateResponse]


class FleetTrackingResponse(BaseModel):
    """Response for fleet-wide tracking dashboard"""

    active_trips: List[TripTrackingResponse]
    total_active_trips: int
    delayed_trips: int
    on_time_trips: int
    completed_trips_today: int
    cancelled_trips_today: int

    # Summary statistics
    average_delay_minutes: Optional[Decimal]
    on_time_percentage: Optional[Decimal]


class DelayAlertRequest(BaseModel):
    """Request to create delay alert"""

    trip_id: str
    delay_minutes: int = Field(..., ge=1, description="Delay in minutes")
    reason: Optional[str] = Field(None, description="Reason for delay")
    estimated_arrival: Optional[datetime] = Field(
        None, description="New estimated arrival"
    )


class DelayAlertResponse(BaseModel):
    """Response for delay alert"""

    success: bool
    message: str
    trip_id: str
    delay_minutes: int
    notifications_sent: int
    affected_passengers: int
