"""
Payment schemas for API requests and responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class PaymentMethodEnum(str, Enum):
    """Payment method enumeration"""
    MPESA = "mpesa"
    CARD = "card"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatusEnum(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"


class RefundStatusEnum(str, Enum):
    """Refund status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundReasonEnum(str, Enum):
    """Refund reason enumeration"""
    TRIP_CANCELLED_BY_OPERATOR = "trip_cancelled_by_operator"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    WEATHER_CONDITIONS = "weather_conditions"
    PASSENGER_REQUEST = "passenger_request"
    DUPLICATE_BOOKING = "duplicate_booking"
    SYSTEM_ERROR = "system_error"
    OTHER = "other"


# Request Schemas
class PaymentInitiateRequest(BaseModel):
    """Request schema for initiating M-Pesa payment"""
    
    booking_id: str = Field(..., description="Booking ID to pay for")
    phone_number: str = Field(..., description="Phone number for M-Pesa payment")
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Payment amount")
    
    @validator("phone_number")
    def validate_phone_number(cls, v):
        # Remove spaces and special characters
        phone = "".join(filter(str.isdigit, v.replace("+", "")))
        
        # Validate length and format
        if len(phone) < 9 or len(phone) > 15:
            raise ValueError("Invalid phone number length")
        
        # Ensure it's a valid Kenyan number for M-Pesa
        if not (phone.startswith("254") or phone.startswith("0")):
            raise ValueError("Phone number must be a valid Kenyan number")
        
        return phone
    
    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        if v > 999999.99:
            raise ValueError("Payment amount too large")
        return v


class PaymentStatusRequest(BaseModel):
    """Request schema for checking payment status"""
    
    payment_id: Optional[str] = Field(None, description="Payment ID")
    checkout_request_id: Optional[str] = Field(None, description="M-Pesa checkout request ID")
    payment_reference: Optional[str] = Field(None, description="Payment reference")
    
    @validator("*", pre=True)
    def validate_at_least_one(cls, v, values):
        if not any([values.get("payment_id"), values.get("checkout_request_id"), values.get("payment_reference")]):
            raise ValueError("At least one identifier must be provided")
        return v


class RefundInitiateRequest(BaseModel):
    """Request schema for initiating refund"""
    
    payment_id: str = Field(..., description="Original payment ID")
    refund_amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Refund amount")
    refund_reason: RefundReasonEnum = Field(..., description="Reason for refund")
    refund_notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    @validator("refund_amount")
    def validate_refund_amount(cls, v):
        if v <= 0:
            raise ValueError("Refund amount must be positive")
        return v


# Response Schemas
class PaymentInitiateResponse(BaseModel):
    """Response schema for payment initiation"""
    
    success: bool
    payment_id: str
    checkout_request_id: Optional[str] = None
    merchant_request_id: Optional[str] = None
    payment_reference: str
    message: str
    expires_at: Optional[datetime] = None


class PaymentStatusResponse(BaseModel):
    """Response schema for payment status"""
    
    payment_id: str
    booking_id: str
    payment_reference: str
    phone_number: str
    amount: Decimal
    status: PaymentStatusEnum
    mpesa_receipt_number: Optional[str] = None
    transaction_date: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class PaymentListResponse(BaseModel):
    """Response schema for payment list"""
    
    payments: List[PaymentStatusResponse]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class RefundStatusResponse(BaseModel):
    """Response schema for refund status"""
    
    refund_id: str
    original_payment_id: str
    booking_id: str
    refund_amount: Decimal
    refund_reason: RefundReasonEnum
    refund_notes: Optional[str] = None
    status: RefundStatusEnum
    mpesa_transaction_id: Optional[str] = None
    requires_approval: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaymentDashboardResponse(BaseModel):
    """Response schema for payment dashboard"""
    
    total_payments: int
    total_amount: Decimal
    successful_payments: int
    failed_payments: int
    pending_payments: int
    success_rate: float
    average_amount: Decimal
    today_payments: int
    today_amount: Decimal
    recent_payments: List[PaymentStatusResponse]


class PaymentAnalyticsResponse(BaseModel):
    """Response schema for payment analytics"""
    
    period: str
    total_revenue: Decimal
    transaction_count: int
    success_rate: float
    average_transaction: Decimal
    payment_methods: Dict[str, int]
    daily_trends: List[Dict[str, Any]]
    hourly_distribution: List[Dict[str, Any]]


# Webhook Schemas
class MpesaCallbackRequest(BaseModel):
    """Schema for M-Pesa STK Push callback"""
    
    Body: Dict[str, Any]
    
    class Config:
        extra = "allow"


class MpesaCallbackResponse(BaseModel):
    """Response schema for M-Pesa callback"""
    
    ResultCode: int = 0
    ResultDesc: str = "Success"


# Receipt Schemas
class ReceiptGenerateRequest(BaseModel):
    """Request schema for generating receipt"""
    
    payment_id: str = Field(..., description="Payment ID")
    delivery_methods: List[str] = Field(default=["email"], description="Delivery methods")
    
    @validator("delivery_methods")
    def validate_delivery_methods(cls, v):
        valid_methods = ["email", "sms"]
        for method in v:
            if method not in valid_methods:
                raise ValueError(f"Invalid delivery method: {method}")
        return v


class ReceiptResponse(BaseModel):
    """Response schema for receipt"""
    
    receipt_id: str
    payment_id: str
    receipt_number: str
    receipt_type: str
    pdf_file_path: Optional[str] = None
    qr_code_data: Optional[str] = None
    email_sent: bool
    sms_sent: bool
    verification_hash: Optional[str] = None
    created_at: datetime


class ReceiptVerificationRequest(BaseModel):
    """Request schema for receipt verification"""
    
    qr_code_data: str = Field(..., description="QR code data from receipt")


class ReceiptVerificationResponse(BaseModel):
    """Response schema for receipt verification"""
    
    valid: bool
    receipt_id: Optional[str] = None
    payment_id: Optional[str] = None
    receipt_number: Optional[str] = None
    amount: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    verification_count: int = 0
    message: str
