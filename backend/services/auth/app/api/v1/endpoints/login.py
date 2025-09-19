"""
Login endpoints for user authentication
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.login_service import login_service
from app.utils.phone_validator import PhoneValidator
from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class LoginInitiateRequest(BaseModel):
    """Request model for login initiation"""

    phone: str = Field(..., description="Phone number in international format")


class LoginInitiateResponse(BaseModel):
    """Response model for login initiation"""

    message: str
    phone: str
    expires_at: str
    resend_available_at: str


class LoginVerifyRequest(BaseModel):
    """Request model for login verification"""

    phone: str = Field(..., description="Phone number in international format")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class UserResponse(BaseModel):
    """User data in login response"""

    id: str
    user_id: str
    phone: str
    first_name: str
    last_name: str
    email: str = None
    role: str


class LoginVerifyResponse(BaseModel):
    """Response model for login verification"""

    message: str
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""

    refresh_token: str = Field(..., description="Valid refresh token")


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh"""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class LogoutResponse(BaseModel):
    """Response model for logout"""

    message: str


@router.post(
    "/login/initiate",
    response_model=LoginInitiateResponse,
    summary="Initiate login process",
    description="Send OTP to user's phone number to start login process",
)
def initiate_login(request: LoginInitiateRequest, db: Session = Depends(get_db)):
    """
    Initiate login by sending OTP to phone number

    Args:
        request: Login initiation request
        db: Database session

    Returns:
        Login initiation response

    Raises:
        HTTPException: If login initiation fails
    """
    try:
        # Validate phone number
        phone = PhoneValidator.validate_and_format(request.phone)

        # Initiate login
        success, response_data = login_service.initiate_login(phone, db)

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "USER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            elif error_code == "ACCOUNT_INACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response_data["message"],
                )
            elif error_code == "RATE_LIMITED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return LoginInitiateResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login initiation failed",
        )


@router.post(
    "/login/verify",
    response_model=LoginVerifyResponse,
    summary="Verify login OTP",
    description="Verify OTP and complete login process",
)
def verify_login(request: LoginVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and complete login

    Args:
        request: Login verification request
        db: Database session

    Returns:
        Login verification response with tokens

    Raises:
        HTTPException: If login verification fails
    """
    try:
        # Validate phone number
        phone = PhoneValidator.validate_and_format(request.phone)

        # Verify login
        success, response_data = login_service.verify_login(phone, request.otp, db)

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code in ["OTP_EXPIRED", "INVALID_OTP", "MAX_ATTEMPTS"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_data["message"],
                )
            elif error_code == "USER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return LoginVerifyResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login verification failed",
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token

    Args:
        request: Token refresh request
        db: Database session

    Returns:
        New tokens

    Raises:
        HTTPException: If token refresh fails
    """
    try:
        # Refresh tokens
        success, response_data = login_service.refresh_tokens(request.refresh_token, db)

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code in ["INVALID_TOKEN_TYPE", "TOKEN_REVOKED"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=response_data["message"],
                )
            elif error_code == "USER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return RefreshTokenResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user",
    description="Logout user by invalidating refresh token",
)
def logout_user(current_user=Depends(get_current_user)):
    """
    Logout current user

    Args:
        current_user: Current authenticated user

    Returns:
        Logout response

    Raises:
        HTTPException: If logout fails
    """
    try:
        # Logout user
        success, response_data = login_service.logout(str(current_user.user_id))

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data["message"],
            )

        return LogoutResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )
