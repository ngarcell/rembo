"""
Authentication endpoints for registration and login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.auth import (
    RegistrationInitiateRequest,
    RegistrationInitiateResponse,
    RegistrationVerifyRequest,
    RegistrationVerifyResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    ErrorResponse
)
from app.services.registration_service import registration_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/register/initiate",
    response_model=RegistrationInitiateResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate user registration",
    description="Start the registration process by sending OTP to phone number"
)
def initiate_registration(
    request: RegistrationInitiateRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate user registration by sending OTP to phone number
    
    - **phone**: Phone number in any format (will be normalized)
    
    Returns OTP expiry time and resend availability
    """
    try:
        success, data = registration_service.initiate_registration(
            request.phone, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data
            )
        
        return RegistrationInitiateResponse(
            success=True,
            message=data["message"],
            phone=data["phone"],
            expires_at=data["expires_at"],
            resend_available_at=data["resend_available_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )

@router.post(
    "/register/verify",
    response_model=RegistrationVerifyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Verify OTP and complete registration",
    description="Verify the OTP code and create user account"
)
def verify_registration(
    request: RegistrationVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and complete user registration
    
    - **phone**: Phone number used for registration
    - **otp**: 6-digit verification code received via SMS
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **email**: User's email address (optional)
    
    Returns user details and authentication tokens
    """
    try:
        success, data = registration_service.verify_registration(
            request.phone,
            request.otp,
            request.first_name,
            request.last_name,
            request.email,
            db
        )
        
        if not success:
            status_code = status.HTTP_400_BAD_REQUEST
            if data.get("error_code") == "OTP_EXPIRED":
                status_code = status.HTTP_410_GONE
            elif data.get("error_code") == "MAX_ATTEMPTS":
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            
            raise HTTPException(status_code=status_code, detail=data)
        
        return RegistrationVerifyResponse(
            success=True,
            message=data["message"],
            user_id=data["user_id"],
            phone=data["phone"],
            access_token=data["access_token"],
            refresh_token=data["refresh_token"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )

@router.post(
    "/register/resend",
    response_model=ResendOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend OTP",
    description="Resend verification code to phone number"
)
def resend_otp(
    request: ResendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Resend OTP for registration
    
    - **phone**: Phone number to resend OTP to
    
    Returns new OTP expiry time and resend availability
    """
    try:
        success, data = registration_service.resend_otp(request.phone, db)
        
        if not success:
            status_code = status.HTTP_400_BAD_REQUEST
            if data.get("error_code") == "RESEND_RATE_LIMITED":
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            
            raise HTTPException(status_code=status_code, detail=data)
        
        return ResendOTPResponse(
            success=True,
            message=data["message"],
            expires_at=data["expires_at"],
            resend_available_at=data["resend_available_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP resend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )
