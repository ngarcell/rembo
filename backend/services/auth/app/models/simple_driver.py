"""
Simple Driver model that matches the actual database schema
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class SimpleDriver(Base):
    """Simple Driver model that matches the actual database schema"""

    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    driver_code = Column(String(20), unique=True, nullable=False)
    license_number = Column(String(50), nullable=False)
    license_expiry = Column(Date, nullable=True)
    fleet_id = Column(UUID(as_uuid=True), ForeignKey("fleets.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Driver(id={self.id}, driver_code='{self.driver_code}')>"

    def to_dict(self):
        """Convert driver to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "driver_code": self.driver_code,
            "license_number": self.license_number,
            "license_expiry": (
                self.license_expiry.isoformat() if self.license_expiry else None
            ),
            "fleet_id": str(self.fleet_id) if self.fleet_id else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
