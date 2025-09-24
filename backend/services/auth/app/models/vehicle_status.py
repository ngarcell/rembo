"""
Vehicle status tracking models for maintenance and compliance
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
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


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


class VehicleStatusHistory(Base):
    """Track vehicle status changes over time"""

    __tablename__ = "vehicle_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_status = Column(SQLEnum(VehicleStatusEnum), nullable=True)
    new_status = Column(SQLEnum(VehicleStatusEnum), nullable=False)
    changed_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vehicle = relationship("SimpleVehicle")
    changed_by_user = relationship("UserProfile")


class MaintenanceRecord(Base):
    """Track vehicle maintenance activities"""

    __tablename__ = "maintenance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    maintenance_type = Column(SQLEnum(MaintenanceTypeEnum), nullable=False)
    priority = Column(
        SQLEnum(MaintenancePriorityEnum), default=MaintenancePriorityEnum.MEDIUM
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Scheduling
    scheduled_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Personnel
    assigned_to = Column(String(200), nullable=True)  # Mechanic/Service provider
    performed_by = Column(String(200), nullable=True)
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    # Cost tracking
    estimated_cost = Column(Integer, nullable=True)  # In cents
    actual_cost = Column(Integer, nullable=True)  # In cents

    # Status
    is_completed = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    # Metadata
    odometer_reading = Column(Integer, nullable=True)  # Kilometers
    next_service_km = Column(Integer, nullable=True)  # Next service at this km
    next_service_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    creator = relationship("UserProfile")


class VehicleDocument(Base):
    """Track vehicle documents and compliance"""

    __tablename__ = "vehicle_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type = Column(
        String(100), nullable=False
    )  # insurance, registration, inspection, etc.
    document_number = Column(String(100), nullable=True)
    issuer = Column(String(200), nullable=True)

    # Dates
    issued_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)

    # File storage
    file_path = Column(String(500), nullable=True)  # Path to stored document
    file_name = Column(String(200), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    uploader = relationship("UserProfile")


class VehicleInspection(Base):
    """Track vehicle inspections and safety checks"""

    __tablename__ = "vehicle_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inspection_type = Column(
        String(100), nullable=False
    )  # safety, emissions, annual, etc.
    inspector_name = Column(String(200), nullable=True)
    inspection_station = Column(String(200), nullable=True)

    # Results
    passed = Column(Boolean, nullable=True)
    score = Column(Integer, nullable=True)  # If applicable

    # Dates
    inspection_date = Column(DateTime, nullable=False)
    next_inspection_date = Column(DateTime, nullable=True)

    # Details
    findings = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    certificate_number = Column(String(100), nullable=True)

    # Metadata
    odometer_reading = Column(Integer, nullable=True)
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    creator = relationship("UserProfile")
