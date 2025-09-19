"""
Fleet model for managing matatu fleets
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Fleet(Base):
    """Fleet model for managing matatu fleets"""

    __tablename__ = "fleets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    manager_id = Column(UUID(as_uuid=True), nullable=True)  # References user_profiles(id)
    fleet_code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # managers = relationship("UserProfile", back_populates="fleet", foreign_keys="UserProfile.fleet_id")
    # vehicles = relationship("Vehicle", back_populates="fleet")

    def __repr__(self):
        return f"<Fleet(id={self.id}, name='{self.name}', active={self.is_active})>"

    def to_dict(self):
        """Convert fleet to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "manager_id": str(self.manager_id) if self.manager_id else None,
            "fleet_code": self.fleet_code,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
