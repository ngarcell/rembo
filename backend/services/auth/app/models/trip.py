"""
Trip and Route Models for Trip Creation & Scheduling
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    Time,
    ARRAY,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class TripStatus(str, enum.Enum):
    """Trip status enumeration"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Route(Base):
    """Route model for trip planning"""

    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Route Information
    route_code = Column(String(20), nullable=False, index=True)
    route_name = Column(String(255), nullable=False)
    origin_name = Column(String(255), nullable=False)
    destination_name = Column(String(255), nullable=False)

    # Route Details
    distance_km = Column(Numeric(8, 2), nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    base_fare = Column(Numeric(10, 2), nullable=False)

    # Optional route data
    waypoints = Column(Text, nullable=True)  # JSON string of waypoints
    description = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    trips = relationship("Trip", back_populates="route", cascade="all, delete-orphan")
    trip_templates = relationship(
        "TripTemplate", back_populates="route", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "fleet_id": str(self.fleet_id),
            "route_code": self.route_code,
            "route_name": self.route_name,
            "origin_name": self.origin_name,
            "destination_name": self.destination_name,
            "distance_km": float(self.distance_km) if self.distance_km else None,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "base_fare": float(self.base_fare),
            "waypoints": self.waypoints,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Trip(Base):
    """Trip model for scheduled transportation services"""

    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    route_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_assignments.id", ondelete="SET NULL"),
        nullable=True,
    )
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    # Trip Code
    trip_code = Column(String(50), nullable=False, unique=True, index=True)

    # Schedule Information
    scheduled_departure = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)

    # Trip Details
    fare = Column(Numeric(10, 2), nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    booked_seats = Column(Integer, default=0, nullable=False)

    # Status and Notes
    status = Column(
        String(20), nullable=False, default=TripStatus.SCHEDULED.value, index=True
    )
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    route = relationship("Route", back_populates="trips")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "scheduled_arrival IS NULL OR scheduled_arrival > scheduled_departure",
            name="valid_trip_times",
        ),
        CheckConstraint(
            "actual_arrival IS NULL OR actual_departure IS NULL OR actual_arrival >= actual_departure",
            name="valid_actual_times",
        ),
        CheckConstraint(
            "available_seats <= total_seats AND available_seats >= 0",
            name="valid_seat_count",
        ),
        CheckConstraint(
            "booked_seats >= 0 AND booked_seats <= total_seats",
            name="valid_booked_seats",
        ),
        CheckConstraint(
            "available_seats + booked_seats = total_seats",
            name="seat_count_consistency",
        ),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "route_id": str(self.route_id),
            "vehicle_id": str(self.vehicle_id),
            "driver_id": str(self.driver_id),
            "assignment_id": str(self.assignment_id) if self.assignment_id else None,
            "fleet_id": str(self.fleet_id),
            "trip_code": self.trip_code,
            "scheduled_departure": (
                self.scheduled_departure.isoformat()
                if self.scheduled_departure
                else None
            ),
            "scheduled_arrival": (
                self.scheduled_arrival.isoformat() if self.scheduled_arrival else None
            ),
            "actual_departure": (
                self.actual_departure.isoformat() if self.actual_departure else None
            ),
            "actual_arrival": (
                self.actual_arrival.isoformat() if self.actual_arrival else None
            ),
            "fare": float(self.fare),
            "total_seats": self.total_seats,
            "available_seats": self.available_seats,
            "booked_seats": self.booked_seats,
            "status": self.status,
            "notes": self.notes,
            "cancellation_reason": self.cancellation_reason,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TripTemplate(Base):
    """Trip template for recurring trip scheduling"""

    __tablename__ = "trip_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    route_id = Column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    fleet_id = Column(
        UUID(as_uuid=True), ForeignKey("fleets.id", ondelete="CASCADE"), nullable=False
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    # Template Information
    template_name = Column(String(255), nullable=False)
    departure_time = Column(Time, nullable=False)
    fare = Column(Numeric(10, 2), nullable=False)

    # Recurrence Pattern
    days_of_week = Column(ARRAY(Integer), nullable=False)  # [1,2,3,4,5] for weekdays

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    route = relationship("Route", back_populates="trip_templates")

    def to_dict(self):
        return {
            "id": str(self.id),
            "route_id": str(self.route_id),
            "fleet_id": str(self.fleet_id),
            "template_name": self.template_name,
            "departure_time": (
                self.departure_time.strftime("%H:%M:%S")
                if self.departure_time
                else None
            ),
            "fare": float(self.fare),
            "days_of_week": self.days_of_week,
            "is_active": self.is_active,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
