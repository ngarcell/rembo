"""
Phone number validation utilities
"""

import re
from typing import Optional, Tuple
from app.core.config import settings


class PhoneValidator:
    """Phone number validation and formatting"""

    # Kenyan phone number patterns
    KENYAN_PATTERNS = [
        r"^(\+254|254|0)(7[0-9]{8})$",  # Safaricom, Airtel
        r"^(\+254|254|0)(1[0-9]{8})$",  # Telkom
    ]

    @classmethod
    def normalize_phone(cls, phone: str) -> str:
        """
        Normalize phone number to international format

        Args:
            phone: Raw phone number input

        Returns:
            Normalized phone number in +254XXXXXXXXX format
        """
        # Remove all non-digit characters except +
        phone = re.sub(r"[^\d+]", "", phone.strip())

        # Handle different formats
        if phone.startswith("+254"):
            return phone
        elif phone.startswith("254"):
            return f"+{phone}"
        elif phone.startswith("0"):
            return f"+254{phone[1:]}"
        elif len(phone) == 9:  # Assume Kenyan number without prefix
            return f"+254{phone}"
        else:
            return phone

    @classmethod
    def validate_phone(cls, phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate phone number format

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, normalized_phone, error_message)
        """
        if not phone:
            return False, None, "Phone number is required"

        # Normalize the phone number
        normalized = cls.normalize_phone(phone)

        # Check length
        if len(normalized) != settings.PHONE_NUMBER_LENGTH:
            return (
                False,
                None,
                f"Phone number must be {settings.PHONE_NUMBER_LENGTH} digits including country code",
            )

        # Check against Kenyan patterns
        is_valid = any(re.match(pattern, normalized) for pattern in cls.KENYAN_PATTERNS)

        if not is_valid:
            return False, None, "Invalid Kenyan phone number format"

        return True, normalized, None

    @classmethod
    def format_for_display(cls, phone: str) -> str:
        """
        Format phone number for display

        Args:
            phone: Normalized phone number

        Returns:
            Formatted phone number for display
        """
        if phone.startswith("+254"):
            # Format as +254 7XX XXX XXX
            digits = phone[4:]  # Remove +254
            if len(digits) == 9:
                return f"+254 {digits[:3]} {digits[3:6]} {digits[6:]}"

        return phone

    @classmethod
    def format_for_sms(cls, phone: str) -> str:
        """
        Format phone number for SMS sending

        Args:
            phone: Normalized phone number

        Returns:
            Phone number formatted for SMS API
        """
        # Africa's Talking expects +254XXXXXXXXX format
        return cls.normalize_phone(phone)
