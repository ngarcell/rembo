"""
Login service for handling user authentication workflow
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.supabase_client import supabase_client
from app.models.user_profile import UserProfile
from app.utils.otp_generator import OTPGenerator
from app.utils.phone_validator import PhoneValidator
from app.services.sms_service import sms_service
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)


class LoginService:
    """Service for handling user login"""

    def __init__(self):
        """Initialize login service"""
        self.supabase_client = supabase_client
        logger.info("Login service initialized")

    def initiate_login(self, phone: str, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """
        Initiate login process by sending OTP

        Args:
            phone: Validated phone number
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Check if user exists
            user = self._get_user_by_phone(phone, db)
            if not user:
                return False, {
                    "message": "Phone number not registered",
                    "error_code": "USER_NOT_FOUND",
                }

            # Check if user is active
            if not user.is_active:
                return False, {
                    "message": "Account is deactivated. Please contact support.",
                    "error_code": "ACCOUNT_INACTIVE",
                }

            # Check rate limiting
            rate_limit_key = f"login_rate_limit:{phone}"
            attempts = redis_client.get(rate_limit_key)
            if attempts and int(attempts) >= settings.RATE_LIMIT_REQUESTS:
                return False, {
                    "message": "Too many login attempts. Please try again later.",
                    "error_code": "RATE_LIMITED",
                }

            # Generate and store OTP
            otp = OTPGenerator.generate_otp()
            otp_hash = OTPGenerator.create_otp_hash(phone, otp)

            # Store OTP data in Redis
            otp_key = f"login_otp:{phone}"
            otp_data = {
                "hash": otp_hash,
                "attempts": 0,
                "user_id": str(user.user_id),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Store with expiration
            redis_client.set(otp_key, otp_data, expire=settings.OTP_EXPIRE_MINUTES * 60)

            # Send OTP via SMS
            sms_success, sms_error = sms_service.send_login_otp(
                phone, otp, user.first_name
            )
            if not sms_success:
                logger.error(f"Failed to send login OTP to {phone}: {sms_error}")
                return False, {
                    "message": "Failed to send verification code. Please try again.",
                    "error_code": "SMS_FAILED",
                }

            # Update rate limiting
            redis_client.incr(rate_limit_key)
            redis_client.expire(rate_limit_key, settings.RATE_LIMIT_WINDOW_MINUTES * 60)

            # Calculate expiry times
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.OTP_EXPIRE_MINUTES
            )
            resend_available_at = datetime.utcnow() + timedelta(
                minutes=1
            )  # 1 minute cooldown

            return True, {
                "message": "Login verification code sent successfully",
                "phone": PhoneValidator.format_for_display(phone),
                "expires_at": expires_at,
                "resend_available_at": resend_available_at,
            }

        except Exception as e:
            logger.error(f"Login initiation error: {e}")
            return False, {
                "message": "Login failed. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }

    def verify_login(
        self, phone: str, otp: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify OTP and complete login

        Args:
            phone: Phone number
            otp: OTP code
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get OTP data from Redis
            otp_key = f"login_otp:{phone}"
            otp_data = redis_client.get(otp_key)

            if not otp_data:
                return False, {
                    "message": "Verification code expired or not found",
                    "error_code": "OTP_EXPIRED",
                }

            # Check attempts
            if otp_data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                redis_client.delete(otp_key)
                return False, {
                    "message": "Too many verification attempts. Please request a new code.",
                    "error_code": "MAX_ATTEMPTS",
                }

            # Verify OTP
            if not OTPGenerator.verify_otp_hash(phone, otp, otp_data["hash"]):
                # Increment attempts
                otp_data["attempts"] += 1
                redis_client.set(
                    otp_key, otp_data, expire=settings.OTP_EXPIRE_MINUTES * 60
                )

                return False, {
                    "message": "Invalid verification code",
                    "error_code": "INVALID_OTP",
                }

            # Get user from database
            user = self._get_user_by_phone(phone, db)
            if not user or not user.is_active:
                redis_client.delete(otp_key)
                return False, {
                    "message": "User account not found or inactive",
                    "error_code": "USER_NOT_FOUND",
                }

            # Generate JWT tokens
            access_token = jwt_service.create_access_token(
                user_id=str(user.user_id), phone=user.phone, role=user.role.value
            )

            refresh_token = jwt_service.create_refresh_token(user_id=str(user.user_id))

            # Update last login timestamp
            user.updated_at = datetime.utcnow()
            db.commit()

            # Clean up OTP
            redis_client.delete(otp_key)

            # Store refresh token in Redis for tracking
            refresh_key = f"refresh_token:{user.user_id}"
            redis_client.set(
                refresh_key,
                refresh_token,
                expire=settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
            )

            logger.info(f"User login successful: {user.id}")

            return True, {
                "message": "Login successful",
                "user": {
                    "id": str(user.id),
                    "user_id": str(user.user_id),
                    "phone": PhoneValidator.format_for_display(user.phone),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role.value,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            }

        except Exception as e:
            logger.error(f"Login verification error: {e}")
            return False, {
                "message": "Login failed. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }

    def refresh_tokens(
        self, refresh_token: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Verify refresh token
            payload = jwt_service.verify_token(refresh_token)

            if payload.get("type") != "refresh":
                return False, {
                    "message": "Invalid token type",
                    "error_code": "INVALID_TOKEN_TYPE",
                }

            user_id = payload.get("sub")

            # Check if refresh token is still valid in Redis
            refresh_key = f"refresh_token:{user_id}"
            stored_token = redis_client.get(refresh_key)

            if not stored_token or stored_token != refresh_token:
                return False, {
                    "message": "Refresh token has been revoked",
                    "error_code": "TOKEN_REVOKED",
                }

            # Get user from database
            user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if not user or not user.is_active:
                return False, {
                    "message": "User not found or inactive",
                    "error_code": "USER_NOT_FOUND",
                }

            # Generate new tokens
            new_access_token = jwt_service.create_access_token(
                user_id=str(user.user_id), phone=user.phone, role=user.role.value
            )

            new_refresh_token = jwt_service.create_refresh_token(
                user_id=str(user.user_id)
            )

            # Update refresh token in Redis
            redis_client.set(
                refresh_key,
                new_refresh_token,
                expire=settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
            )

            logger.info(f"Tokens refreshed for user: {user.id}")

            return True, {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            }

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False, {
                "message": "Token refresh failed",
                "error_code": "REFRESH_FAILED",
            }

    def logout(self, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Logout user by invalidating refresh token

        Args:
            user_id: User's unique identifier

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Remove refresh token from Redis
            refresh_key = f"refresh_token:{user_id}"
            redis_client.delete(refresh_key)

            logger.info(f"User logged out: {user_id}")

            return True, {"message": "Logout successful"}

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, {
                "message": "Logout failed",
                "error_code": "LOGOUT_FAILED",
            }

    def _get_user_by_phone(self, phone: str, db: Session) -> Optional[UserProfile]:
        """Get user by phone number"""
        return db.query(UserProfile).filter(UserProfile.phone == phone).first()


# Create global login service instance
login_service = LoginService()
