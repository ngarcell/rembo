"""
Registration service for handling user registration workflow
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.supabase_client import supabase_client
from app.models.user_profile import UserProfile, UserRole
from app.utils.otp_generator import OTPGenerator
from app.utils.phone_validator import PhoneValidator
from app.services.sms_service import sms_service

logger = logging.getLogger(__name__)


class RegistrationService:
    """Service for handling user registration"""

    def __init__(self):
        """Initialize registration service"""
        # Use the global Supabase client
        self.supabase_client = supabase_client
        logger.info("Registration service initialized with Supabase client")

    def initiate_registration(
        self, phone: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Initiate registration process by sending OTP

        Args:
            phone: Validated phone number
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Check if phone already exists
            existing_user = self._get_user_by_phone(phone, db)
            if existing_user:
                return False, {
                    "message": "Phone number already registered",
                    "error_code": "PHONE_EXISTS",
                }

            # Check rate limiting
            rate_limit_key = f"registration_rate_limit:{phone}"
            attempts = redis_client.get(rate_limit_key)
            if attempts and int(attempts) >= settings.RATE_LIMIT_REQUESTS:
                return False, {
                    "message": "Too many registration attempts. Please try again later.",
                    "error_code": "RATE_LIMITED",
                }

            # Generate and store OTP
            otp = OTPGenerator.generate_otp()
            otp_hash = OTPGenerator.create_otp_hash(phone, otp)

            # Store OTP data in Redis
            otp_key = f"registration_otp:{phone}"
            otp_data = {
                "hash": otp_hash,
                "attempts": 0,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Store with expiration
            redis_client.set(otp_key, otp_data, expire=settings.OTP_EXPIRE_MINUTES * 60)

            # Send OTP via SMS
            sms_success, sms_error = sms_service.send_otp(phone, otp)
            if not sms_success:
                logger.error(f"Failed to send OTP to {phone}: {sms_error}")
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
                "message": "Verification code sent successfully",
                "phone": PhoneValidator.format_for_display(phone),
                "expires_at": expires_at,
                "resend_available_at": resend_available_at,
            }

        except Exception as e:
            logger.error(f"Registration initiation error: {e}")
            return False, {
                "message": "Registration failed. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }

    def verify_registration(
        self,
        phone: str,
        otp: str,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify OTP and complete registration

        Args:
            phone: Phone number
            otp: OTP code
            first_name: User's first name
            last_name: User's last name
            email: User's email
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get OTP data from Redis
            otp_key = f"registration_otp:{phone}"
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

            # Check if user already exists (race condition protection)
            existing_user = self._get_user_by_phone(phone, db)
            if existing_user:
                redis_client.delete(otp_key)
                return False, {
                    "message": "Phone number already registered",
                    "error_code": "PHONE_EXISTS",
                }

            # Create user in Supabase Auth
            supabase_user = None
            if self.supabase_client.service_client:
                try:
                    auth_response = self.supabase_client.service_client.auth.admin.create_user(
                        {
                            "phone": phone,
                            "email": (
                                email
                                if email
                                else f"{phone.replace('+', '')}@temp.matatu.app"
                            ),
                            "phone_confirmed": True,
                            "email_confirmed": bool(email),
                        }
                    )
                    supabase_user = auth_response.user
                    logger.info(f"Created Supabase user: {supabase_user.id}")

                    # Also create user profile in Supabase profiles table
                    profile_data = {
                        "user_id": supabase_user.id,  # This should be user_id, not id
                        "phone": phone,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "role": UserRole.PASSENGER.value,
                        "is_active": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }

                    self.supabase_client.create_user_profile(profile_data)
                    logger.info(f"Created Supabase profile for user: {supabase_user.id}")

                except Exception as e:
                    logger.error(f"Supabase user creation failed: {e}")
                    return False, {
                        "message": "Account creation failed. Please try again.",
                        "error_code": "AUTH_FAILED",
                    }

            # Create user profile in local database
            user_profile = UserProfile(
                user_id=supabase_user.id if supabase_user else uuid.uuid4(),
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=UserRole.PASSENGER.value,
                is_active=True,
            )

            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)

            # Clean up OTP
            redis_client.delete(otp_key)

            # Send welcome message
            sms_service.send_welcome_message(phone, first_name)

            # Generate tokens (simplified for now)
            access_token = None
            refresh_token = None

            logger.info(f"User registration completed: {user_profile.id}")

            return True, {
                "message": "Registration completed successfully",
                "user_id": str(user_profile.id),
                "phone": PhoneValidator.format_for_display(phone),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

        except Exception as e:
            logger.error(f"Registration verification error: {e}")
            db.rollback()
            return False, {
                "message": "Registration failed. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }

    def resend_otp(self, phone: str, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """
        Resend OTP for registration

        Args:
            phone: Phone number
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Check if user already exists
            existing_user = self._get_user_by_phone(phone, db)
            if existing_user:
                return False, {
                    "message": "Phone number already registered",
                    "error_code": "PHONE_EXISTS",
                }

            # Check rate limiting for resend
            resend_key = f"resend_rate_limit:{phone}"
            resend_attempts = redis_client.get(resend_key)
            if resend_attempts and int(resend_attempts) >= 3:  # Max 3 resends per hour
                return False, {
                    "message": "Too many resend attempts. Please try again later.",
                    "error_code": "RESEND_RATE_LIMITED",
                }

            # Generate new OTP
            otp = OTPGenerator.generate_otp()
            otp_hash = OTPGenerator.create_otp_hash(phone, otp)

            # Store new OTP data
            otp_key = f"registration_otp:{phone}"
            otp_data = {
                "hash": otp_hash,
                "attempts": 0,
                "created_at": datetime.utcnow().isoformat(),
            }

            redis_client.set(otp_key, otp_data, expire=settings.OTP_EXPIRE_MINUTES * 60)

            # Send OTP
            sms_success, sms_error = sms_service.send_otp(phone, otp)
            if not sms_success:
                return False, {
                    "message": "Failed to send verification code. Please try again.",
                    "error_code": "SMS_FAILED",
                }

            # Update resend rate limiting
            redis_client.incr(resend_key)
            redis_client.expire(resend_key, 3600)  # 1 hour

            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.OTP_EXPIRE_MINUTES
            )
            resend_available_at = datetime.utcnow() + timedelta(minutes=1)

            return True, {
                "message": "Verification code resent successfully",
                "expires_at": expires_at,
                "resend_available_at": resend_available_at,
            }

        except Exception as e:
            logger.error(f"OTP resend error: {e}")
            return False, {
                "message": "Failed to resend verification code",
                "error_code": "INTERNAL_ERROR",
            }

    def _get_user_by_phone(self, phone: str, db: Session) -> Optional[UserProfile]:
        """Get user by phone number"""
        return db.query(UserProfile).filter(UserProfile.phone == phone).first()


# Create global registration service instance
registration_service = RegistrationService()
