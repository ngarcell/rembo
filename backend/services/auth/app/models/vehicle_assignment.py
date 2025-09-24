"""
Vehicle Assignment Model for managing driver-vehicle relationships
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VehicleAssignment(Base):
    """Vehicle assignment model for managing driver-vehicle relationships"""

    __tablename__ = "vehicle_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    manager_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True
    )
    fleet_id = Column(
        UUID(as_uuid=True), ForeignKey("fleets.id"), nullable=False, index=True
    )

    # Assignment timing
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    unassigned_at = Column(DateTime, nullable=True)

    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    assignment_notes = Column(Text, nullable=True)

    # System fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VehicleAssignment(id={self.id}, vehicle_id={self.vehicle_id}, driver_id={self.driver_id}, active={self.is_active})>"

    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            "id": str(self.id),
            "vehicle_id": str(self.vehicle_id),
            "driver_id": str(self.driver_id),
            "manager_id": str(self.manager_id),
            "fleet_id": str(self.fleet_id),
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "unassigned_at": (
                self.unassigned_at.isoformat() if self.unassigned_at else None
            ),
            "is_active": self.is_active,
            "assignment_notes": self.assignment_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_response_dict(self, driver_name: str = None, vehicle_info: str = None):
        """Convert assignment to response dictionary with additional info"""
        base_dict = self.to_dict()
        base_dict.update(
            {
                "driver_name": driver_name,
                "vehicle_info": vehicle_info,
            }
        )
        return base_dict

    @property
    def duration_days(self):
        """Calculate assignment duration in days"""
        if not self.assigned_at:
            return 0

        end_date = self.unassigned_at or datetime.utcnow()
        return (end_date - self.assigned_at).days

    def unassign(self, notes: str = None):
        """Unassign the driver from vehicle"""
        self.is_active = False
        self.unassigned_at = datetime.utcnow()
        if notes:
            self.assignment_notes = notes
        self.updated_at = datetime.utcnow()
