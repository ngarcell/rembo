"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.utils.phone_validator import PhoneValidator


class RegistrationInitiateRequest(BaseModel):
    """Request schema for initiating registration"""

    phone: str = Field(..., description="Phone number in any format")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, normalized, error = PhoneValidator.validate_phone(v)
        if not is_valid:
            raise ValueError(error)
        return normalized


class RegistrationInitiateResponse(BaseModel):
    """Response schema for registration initiation"""

    success: bool
    message: str
    phone: str
    expires_at: datetime
    resend_available_at: datetime


class RegistrationVerifyRequest(BaseModel):
    """Request schema for OTP verification"""

    phone: str = Field(..., description="Phone number used for registration")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    first_name: Optional[str] = Field(
        None, max_length=100, description="User's first name"
    )
    last_name: Optional[str] = Field(
        None, max_length=100, description="User's last name"
    )
    email: Optional[str] = Field(None, description="User's email address")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, normalized, error = PhoneValidator.validate_phone(v)
        if not is_valid:
            raise ValueError(error)
        return normalized

    @validator("otp")
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError("OTP must contain only digits")
        return v




class RegistrationVerifyResponse(BaseModel):
    """Response schema for registration verification"""

    success: bool
    message: str
    user_id: Optional[str] = None
    phone: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class ResendOTPRequest(BaseModel):
    """Request schema for resending OTP"""

    phone: str = Field(..., description="Phone number to resend OTP to")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, normalized, error = PhoneValidator.validate_phone(v)
        if not is_valid:
            raise ValueError(error)
        return normalized


class ResendOTPResponse(BaseModel):
    """Response schema for OTP resend"""

    success: bool
    message: str
    expires_at: datetime
    resend_available_at: datetime


class ErrorResponse(BaseModel):
    """Standard error response schema"""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class UserProfileResponse(BaseModel):
    """User profile response schema"""

    id: str
    phone: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
