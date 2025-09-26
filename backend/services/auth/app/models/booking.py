"""
Booking models for passenger seat booking system
"""

import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    Text,
    DECIMAL,
    ARRAY,
    CheckConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    """Booking status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""

    MPESA = "mpesa"
    CARD = "card"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class SeatPreference(str, enum.Enum):
    """Seat preference enumeration"""

    WINDOW = "window"
    AISLE = "aisle"
    FRONT = "front"
    BACK = "back"
    ANY = "any"


class Passenger(Base):
    """Passenger model for booking system"""

    __tablename__ = "passengers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True
    )  # Optional for registered users

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    national_id = Column(String(50), nullable=True)

    # Preferences
    preferred_seat_type = Column(
        String(20), default="ANY", nullable=False
    )  # Use uppercase to match database enum
    loyalty_points = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    bookings = relationship("Booking", back_populates="passenger")
    user = relationship("UserProfile", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Passenger(id={self.id}, name='{self.first_name} {self.last_name}')>"

    def to_dict(self):
        """Convert passenger to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "date_of_birth": (
                self.date_of_birth.isoformat() if self.date_of_birth else None
            ),
            "national_id": self.national_id,
            "preferred_seat_type": self.preferred_seat_type,
            "loyalty_points": self.loyalty_points,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Booking(Base):
    """Booking model for trip reservations"""

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    passenger_id = Column(
        UUID(as_uuid=True),
        ForeignKey("passengers.id", ondelete="CASCADE"),
        nullable=False,
    )
    booking_reference = Column(String(20), unique=True, nullable=False, index=True)

    # Booking Details
    seats_booked = Column(Integer, nullable=False)
    seat_numbers = Column(ARRAY(String), nullable=False)
    total_fare = Column(DECIMAL(10, 2), nullable=False)
    booking_status = Column(
        String(20), default="PENDING", nullable=False
    )  # Use uppercase to match database enum

    # Payment Details
    payment_method = Column(
        String(20), nullable=True
    )  # Temporarily use string instead of enum
    payment_status = Column(
        String(20), default="PENDING", nullable=False
    )  # Use uppercase to match database enum
    amount_paid = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    amount_due = Column(DECIMAL(10, 2), nullable=False)

    # Passenger Details (denormalized for quick access)
    passenger_name = Column(String(200), nullable=False)
    passenger_phone = Column(String(15), nullable=False)
    passenger_email = Column(String(255), nullable=True)
    emergency_contact = Column(String(15), nullable=True)

    # Timestamps
    booking_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("seats_booked > 0", name="positive_seats_booked"),
        CheckConstraint("amount_paid >= 0", name="non_negative_amount_paid"),
        CheckConstraint("amount_due >= 0", name="non_negative_amount_due"),
        CheckConstraint("total_fare > 0", name="positive_total_fare"),
        CheckConstraint(
            "array_length(seat_numbers, 1) = seats_booked",
            name="seat_numbers_match_count",
        ),
    )

    # Relationships
    trip = relationship("Trip", foreign_keys=[trip_id])
    passenger = relationship("Passenger", back_populates="bookings")
    payments = relationship(
        "Payment", back_populates="booking", cascade="all, delete-orphan"
    )
    payment_transactions = relationship(
        "PaymentTransaction", back_populates="booking", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Booking(id={self.id}, reference='{self.booking_reference}')>"

    def to_dict(self):
        """Convert booking to dictionary"""
        return {
            "id": str(self.id),
            "trip_id": str(self.trip_id),
            "passenger_id": str(self.passenger_id),
            "booking_reference": self.booking_reference,
            "seats_booked": self.seats_booked,
            "seat_numbers": self.seat_numbers,
            "total_fare": float(self.total_fare),
            "booking_status": self.booking_status,
            "payment_method": self.payment_method if self.payment_method else None,
            "payment_status": self.payment_status,
            "amount_paid": float(self.amount_paid),
            "amount_due": float(self.amount_due),
            "passenger_name": self.passenger_name,
            "passenger_phone": self.passenger_phone,
            "passenger_email": self.passenger_email,
            "emergency_contact": self.emergency_contact,
            "booking_date": (
                self.booking_date.isoformat() if self.booking_date else None
            ),
            "payment_deadline": (
                self.payment_deadline.isoformat() if self.payment_deadline else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Payment(Base):
    """Payment model for booking transactions"""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Payment Details
    payment_reference = Column(String(50), unique=True, nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="KES", nullable=False)

    # Payment Gateway Details
    gateway_transaction_id = Column(String(100), nullable=True)
    gateway_response = Column(Text, nullable=True)

    # Status
    payment_status = Column(
        SQLEnum(PaymentStatus), default="pending", nullable=False
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (CheckConstraint("amount > 0", name="positive_payment_amount"),)

    # Relationships
    booking = relationship("Booking", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, reference='{self.payment_reference}')>"

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            "id": str(self.id),
            "booking_id": str(self.booking_id),
            "payment_reference": self.payment_reference,
            "payment_method": self.payment_method.value,
            "amount": float(self.amount),
            "currency": self.currency,
            "gateway_transaction_id": self.gateway_transaction_id,
            "gateway_response": self.gateway_response,
            "payment_status": self.payment_status.value,
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
