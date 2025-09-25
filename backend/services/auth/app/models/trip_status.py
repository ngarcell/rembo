"""
Trip Status Tracking Models for Real-time Updates
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Boolean,
    Integer,
    Numeric,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


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


class TripStatusUpdate(Base):
    """Track real-time trip status updates"""

    __tablename__ = "trip_status_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(SQLEnum(TripStatusEnum), nullable=False)

    # Location data
    location_lat = Column(Numeric(10, 8), nullable=True)
    location_lng = Column(Numeric(11, 8), nullable=True)
    location_name = Column(String(255), nullable=True)

    # Timing data
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)
    delay_minutes = Column(Integer, default=0, nullable=False)

    # Update metadata
    update_source = Column(
        SQLEnum(UpdateSourceEnum), default=UpdateSourceEnum.SYSTEM, nullable=False
    )
    notes = Column(Text, nullable=True)
    updated_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    trip = relationship("Trip")
    updater = relationship("UserProfile")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "trip_id": str(self.trip_id),
            "status": self.status.value,
            "location_lat": float(self.location_lat) if self.location_lat else None,
            "location_lng": float(self.location_lng) if self.location_lng else None,
            "location_name": self.location_name,
            "estimated_arrival": (
                self.estimated_arrival.isoformat() if self.estimated_arrival else None
            ),
            "delay_minutes": self.delay_minutes,
            "update_source": self.update_source.value,
            "notes": self.notes,
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "created_at": self.created_at.isoformat(),
        }


class GPSLocation(Base):
    """GPS tracking data for vehicles"""

    __tablename__ = "gps_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # GPS coordinates
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    altitude = Column(Numeric(8, 2), nullable=True)

    # Movement data
    speed_kmh = Column(Numeric(5, 2), nullable=True)
    heading = Column(Numeric(5, 2), nullable=True)  # Compass direction 0-360
    accuracy_meters = Column(Integer, nullable=True)

    # Timestamps
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    trip = relationship("Trip")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "vehicle_id": str(self.vehicle_id),
            "trip_id": str(self.trip_id) if self.trip_id else None,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),
            "altitude": float(self.altitude) if self.altitude else None,
            "speed_kmh": float(self.speed_kmh) if self.speed_kmh else None,
            "heading": float(self.heading) if self.heading else None,
            "accuracy_meters": self.accuracy_meters,
            "recorded_at": self.recorded_at.isoformat(),
            "received_at": self.received_at.isoformat(),
        }


class NotificationPreference(Base):
    """User notification preferences"""

    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Notification channels
    sms_enabled = Column(Boolean, default=True, nullable=False)
    email_enabled = Column(Boolean, default=True, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)

    # Notification types
    trip_status_updates = Column(Boolean, default=True, nullable=False)
    delay_notifications = Column(Boolean, default=True, nullable=False)
    cancellation_alerts = Column(Boolean, default=True, nullable=False)
    booking_confirmations = Column(Boolean, default=True, nullable=False)

    # Timing preferences
    advance_notice_minutes = Column(Integer, default=30, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("UserProfile")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "sms_enabled": self.sms_enabled,
            "email_enabled": self.email_enabled,
            "push_enabled": self.push_enabled,
            "trip_status_updates": self.trip_status_updates,
            "delay_notifications": self.delay_notifications,
            "cancellation_alerts": self.cancellation_alerts,
            "booking_confirmations": self.booking_confirmations,
            "advance_notice_minutes": self.advance_notice_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
