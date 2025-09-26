"""
Payment models for M-Pesa integration and payment processing
"""

import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLEnum
from sqlalchemy import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    MPESA = "mpesa"
    CARD = "card"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class RefundStatus(str, enum.Enum):
    """Refund status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundReason(str, enum.Enum):
    """Refund reason enumeration"""
    TRIP_CANCELLED_BY_OPERATOR = "trip_cancelled_by_operator"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    WEATHER_CONDITIONS = "weather_conditions"
    PASSENGER_REQUEST = "passenger_request"
    DUPLICATE_BOOKING = "duplicate_booking"
    SYSTEM_ERROR = "system_error"
    OTHER = "other"


class PaymentTransaction(Base):
    """Enhanced payment transaction model for M-Pesa integration"""
    
    __tablename__ = "payment_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    
    # M-Pesa specific fields
    checkout_request_id = Column(String(100), unique=True, nullable=True, index=True)
    merchant_request_id = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Transaction tracking
    mpesa_receipt_number = Column(String(100), nullable=True, unique=True)
    transaction_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(PaymentStatus), default="pending", nullable=False)
    
    # Payment metadata
    account_reference = Column(String(50), nullable=True)
    transaction_desc = Column(Text, nullable=True)
    payment_reference = Column(String(50), unique=True, nullable=False, index=True)
    
    # Gateway response data
    gateway_response = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Payment timeout
    
    # Relationships
    booking = relationship("Booking", back_populates="payment_transactions")
    receipts = relationship("PaymentReceipt", back_populates="payment")
    refunds = relationship("RefundTransaction", back_populates="original_payment")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_amount"),
        Index("idx_payment_status_created", "status", "created_at"),
        Index("idx_payment_phone_created", "phone_number", "created_at"),
    )


class PaymentReceipt(Base):
    """Payment receipt model for receipt management"""
    
    __tablename__ = "payment_receipts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False)
    
    # Receipt identification
    receipt_number = Column(String(50), unique=True, nullable=False)
    receipt_type = Column(String(20), default="PAYMENT", nullable=False)
    
    # File management
    pdf_file_path = Column(Text, nullable=True)
    pdf_file_size = Column(Integer, nullable=True)
    qr_code_data = Column(Text, nullable=True)
    
    # Delivery tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Verification
    verification_hash = Column(String(256), nullable=True)
    verification_count = Column(Integer, default=0)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    payment = relationship("PaymentTransaction", back_populates="receipts")
    
    # Constraints
    __table_args__ = (
        Index("idx_receipt_number", "receipt_number"),
        Index("idx_receipt_payment_id", "payment_id"),
    )


class RefundTransaction(Base):
    """Refund transaction model for M-Pesa B2C refunds"""
    
    __tablename__ = "refund_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    original_payment_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    
    # Refund details
    refund_amount = Column(DECIMAL(10, 2), nullable=False)
    refund_reason = Column(SQLEnum(RefundReason), nullable=False)
    refund_notes = Column(Text, nullable=True)
    
    # M-Pesa B2C details
    mpesa_transaction_id = Column(String(100), nullable=True)
    mpesa_conversation_id = Column(String(100), nullable=True)
    mpesa_originator_conversation_id = Column(String(100), nullable=True)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(RefundStatus), default="pending", nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing metadata
    processed_by = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True)
    processing_method = Column(String(20), default="MPESA_B2C", nullable=False)
    
    # Gateway response
    gateway_response = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    original_payment = relationship("PaymentTransaction", back_populates="refunds")
    booking = relationship("Booking")
    approved_by_user = relationship("UserProfile", foreign_keys=[approved_by])
    processed_by_user = relationship("UserProfile", foreign_keys=[processed_by])
    
    # Constraints
    __table_args__ = (
        CheckConstraint("refund_amount > 0", name="check_positive_refund_amount"),
        Index("idx_refund_status_created", "status", "created_at"),
        Index("idx_refund_original_payment", "original_payment_id"),
    )


class PaymentWebhookLog(Base):
    """Log model for M-Pesa webhook callbacks"""
    
    __tablename__ = "payment_webhook_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Webhook details
    checkout_request_id = Column(String(100), nullable=True, index=True)
    webhook_type = Column(String(50), nullable=False)  # 'stk_push', 'b2c', etc.
    
    # Request data
    raw_payload = Column(Text, nullable=False)
    headers = Column(Text, nullable=True)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        Index("idx_webhook_checkout_request", "checkout_request_id"),
        Index("idx_webhook_processed", "processed", "received_at"),
    )
