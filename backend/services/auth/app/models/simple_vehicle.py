"""
Simple Vehicle model that matches the actual database schema
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum

from app.core.database import Base


class VehicleStatus(str, Enum):
    """Vehicle status enumeration"""

    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class SimpleVehicle(Base):
    """Simple Vehicle model that matches the actual database schema"""

    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fleet_id = Column(UUID(as_uuid=True), ForeignKey("fleets.id"), nullable=True)

    # Basic Information
    fleet_number = Column(String(20), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    vehicle_model = Column(String(100), nullable=True)
    year_manufactured = Column(Integer, nullable=True)

    # GPS & Tracking
    gps_device_id = Column(String(100), nullable=True)
    sim_number = Column(String(20), nullable=True)
    gps_api_key = Column(String, nullable=True)  # Text in DB

    # Status
    status = Column(String(20), default=VehicleStatus.ACTIVE.value, nullable=False)

    # System Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Vehicle(id={self.id}, license_plate='{self.license_plate}', fleet_number='{self.fleet_number}')>"

    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            "id": str(self.id),
            "fleet_id": str(self.fleet_id) if self.fleet_id else None,
            "fleet_number": self.fleet_number,
            "license_plate": self.license_plate,
            "capacity": self.capacity,
            "vehicle_model": self.vehicle_model,
            "year_manufactured": self.year_manufactured,
            "gps_device_id": self.gps_device_id,
            "sim_number": self.sim_number,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
