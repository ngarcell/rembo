"""
OTP generation and validation utilities
"""

import secrets
import string
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Tuple, Optional
from app.core.config import settings


class OTPGenerator:
    """OTP generation and validation"""

    @classmethod
    def generate_otp(cls) -> str:
        """
        Generate a random OTP

        Returns:
            OTP string of configured length
        """
        digits = string.digits
        otp = "".join(secrets.choice(digits) for _ in range(settings.OTP_LENGTH))
        return otp

    @classmethod
    def create_otp_hash(cls, phone: str, otp: str) -> str:
        """
        Create a secure hash of OTP for storage

        Args:
            phone: Phone number
            otp: OTP code

        Returns:
            Hashed OTP
        """
        message = f"{phone}:{otp}:{settings.JWT_SECRET_KEY}"
        return hashlib.sha256(message.encode()).hexdigest()

    @classmethod
    def verify_otp_hash(cls, phone: str, otp: str, stored_hash: str) -> bool:
        """
        Verify OTP against stored hash

        Args:
            phone: Phone number
            otp: OTP to verify
            stored_hash: Stored hash to verify against

        Returns:
            True if OTP is valid
        """
        expected_hash = cls.create_otp_hash(phone, otp)
        return hmac.compare_digest(expected_hash, stored_hash)

    @classmethod
    def get_otp_expiry(cls) -> datetime:
        """
        Get OTP expiry timestamp

        Returns:
            Expiry datetime
        """
        return datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    @classmethod
    def is_otp_expired(cls, created_at: datetime) -> bool:
        """
        Check if OTP is expired

        Args:
            created_at: OTP creation timestamp

        Returns:
            True if OTP is expired
        """
        expiry_time = created_at + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        return datetime.utcnow() > expiry_time

    @classmethod
    def format_otp_message(cls, otp: str) -> str:
        """
        Format OTP message for SMS

        Args:
            otp: OTP code

        Returns:
            Formatted SMS message
        """
        return f"Your Matatu Fleet verification code is: {otp}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this code."
