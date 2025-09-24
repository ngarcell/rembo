"""
Vehicle model for managing fleet vehicles
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    Date,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class VehicleStatus(str, Enum):
    """Vehicle status enumeration"""

    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    RETIRED = "retired"
    INSPECTION_DUE = "inspection_due"


class VehicleType(str, Enum):
    """Vehicle type enumeration"""

    MATATU = "matatu"
    BUS = "bus"
    VAN = "van"
    MINIBUS = "minibus"
    COASTER = "coaster"


class Vehicle(Base):
    """Vehicle model for managing fleet vehicles"""

    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fleet_id = Column(UUID(as_uuid=True), ForeignKey("fleets.id"), nullable=False)
    manager_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True
    )

    # Basic Information
    fleet_number = Column(String(20), nullable=False)  # Unique within fleet
    license_plate = Column(
        String(20), unique=True, nullable=False
    )  # Unique across system
    vehicle_type = Column(String(50), nullable=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=False)

    # GPS & Tracking
    gps_device_id = Column(String(100), nullable=True)
    sim_number = Column(String(20), nullable=True)
    gps_api_key = Column(Text, nullable=True)  # Encrypted
    gps_provider = Column(String(100), nullable=True)

    # Operational Details
    route = Column(String(200), nullable=True)
    status = Column(String(20), default=VehicleStatus.ACTIVE, nullable=False)
    registration_date = Column(Date, default=date.today, nullable=True)

    # Insurance & Compliance
    insurance_policy = Column(String(100), nullable=True)
    insurance_expiry = Column(Date, nullable=True)
    last_inspection = Column(Date, nullable=True)
    next_inspection = Column(Date, nullable=True)

    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Vehicle(id={self.id}, license_plate='{self.license_plate}', fleet_number='{self.fleet_number}')>"

    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            "id": str(self.id),
            "fleet_id": str(self.fleet_id),
            "manager_id": str(self.manager_id) if self.manager_id else None,
            "fleet_number": self.fleet_number,
            "license_plate": self.license_plate,
            "vehicle_type": self.vehicle_type,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "capacity": self.capacity,
            "gps_device_id": self.gps_device_id,
            "sim_number": self.sim_number,
            "gps_provider": self.gps_provider,
            "route": self.route,
            "status": self.status,
            "registration_date": (
                self.registration_date.isoformat() if self.registration_date else None
            ),
            "insurance_policy": self.insurance_policy,
            "insurance_expiry": (
                self.insurance_expiry.isoformat() if self.insurance_expiry else None
            ),
            "last_inspection": (
                self.last_inspection.isoformat() if self.last_inspection else None
            ),
            "next_inspection": (
                self.next_inspection.isoformat() if self.next_inspection else None
            ),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_summary_dict(self):
        """Convert vehicle to summary dictionary for listings"""
        return {
            "id": str(self.id),
            "fleet_number": self.fleet_number,
            "license_plate": self.license_plate,
            "vehicle_type": self.vehicle_type,
            "make": self.make,
            "model": self.model,
            "capacity": self.capacity,
            "status": self.status,
            "route": self.route,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def display_name(self):
        """Get display name for vehicle"""
        if self.make and self.model:
            return f"{self.make} {self.model} ({self.license_plate})"
        return f"{self.license_plate}"

    @property
    def is_inspection_due(self):
        """Check if vehicle inspection is due"""
        if not self.next_inspection:
            return False
        return self.next_inspection <= date.today()

    @property
    def is_insurance_expired(self):
        """Check if vehicle insurance is expired"""
        if not self.insurance_expiry:
            return False
        return self.insurance_expiry <= date.today()

    def update_status_based_on_compliance(self):
        """Update vehicle status based on compliance checks"""
        if self.is_inspection_due:
            self.status = VehicleStatus.INSPECTION_DUE
        elif self.is_insurance_expired:
            self.status = VehicleStatus.INACTIVE
        elif self.status == VehicleStatus.INSPECTION_DUE and not self.is_inspection_due:
            self.status = VehicleStatus.ACTIVE
