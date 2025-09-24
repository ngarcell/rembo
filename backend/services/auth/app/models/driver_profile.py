"""
Driver Profile Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class EmploymentStatus(str, enum.Enum):
    """Employment status enumeration"""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class DriverProfile(Base):
    """Driver profile model"""
    
    __tablename__ = "drivers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(String(20), unique=True, nullable=False, index=True)  # DRV-XXXYYY format
    user_id = Column(UUID(as_uuid=True), nullable=True)  # References user_profiles(id) for login
    fleet_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References fleets(id)
    manager_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References user_profiles(id)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=True)
    
    # License Information
    license_number = Column(String(50), unique=True, nullable=False)
    license_class = Column(String(10), nullable=False)  # A, B, C, etc.
    license_expiry = Column(Date, nullable=False)
    
    # Employment Details
    hire_date = Column(Date, nullable=False, default=func.current_date())
    employment_status = Column(String(20), nullable=False, default=EmploymentStatus.ACTIVE.value)
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DriverProfile(id={self.id}, driver_id={self.driver_id}, name={self.first_name} {self.last_name})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "driver_id": self.driver_id,
            "user_id": str(self.user_id) if self.user_id else None,
            "fleet_id": str(self.fleet_id),
            "manager_id": str(self.manager_id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "national_id": self.national_id,
            "license_number": self.license_number,
            "license_class": self.license_class,
            "license_expiry": self.license_expiry.isoformat() if self.license_expiry else None,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "employment_status": self.employment_status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DriverDocument(Base):
    """Driver document model for file storage"""
    
    __tablename__ = "driver_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References drivers(id)
    document_type = Column(String(50), nullable=False)  # license, id_copy, photo, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Supabase Storage path
    file_size = Column(String(20), nullable=True)  # File size in bytes
    mime_type = Column(String(100), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)  # References user_profiles(id)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DriverDocument(id={self.id}, driver_id={self.driver_id}, type={self.document_type})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "driver_id": str(self.driver_id),
            "document_type": self.document_type,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "uploaded_by": str(self.uploaded_by),
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
