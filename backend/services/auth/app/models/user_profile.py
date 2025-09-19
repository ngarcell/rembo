"""
User Profile Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    MANAGER = "manager"
    PASSENGER = "passenger"


class UserProfile(Base):
    """User profile model"""

    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False
    )  # Supabase auth user ID
    phone = Column(String(15), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=UserRole.PASSENGER.value,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    fleet_id = Column(UUID(as_uuid=True), nullable=True)  # Temporarily removed FK constraint
    temporary_access_code = Column(String(20), nullable=True)
    created_by_admin_id = Column(String(36), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    # fleet = relationship("Fleet", back_populates="managers")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, phone={self.phone}, role={self.role})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "fleet_id": str(self.fleet_id) if self.fleet_id else None,
            "temporary_access_code": self.temporary_access_code,
            "created_by_admin_id": self.created_by_admin_id,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
