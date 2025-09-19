"""
SMS service using Africa's Talking API
"""

import africastalking
import logging
from typing import Tuple, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service for sending OTP and notifications"""

    def __init__(self):
        """Initialize Africa's Talking SDK"""
        if settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY:
            try:
                africastalking.initialize(
                    settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_API_KEY
                )
                self.sms = africastalking.SMS
                self.initialized = True
                logger.info("Africa's Talking SMS service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Africa's Talking: {e}")
                self.initialized = False
        else:
            logger.warning(
                "Africa's Talking credentials not configured - SMS will be mocked"
            )
            self.initialized = False

    def send_sms(self, phone: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Send SMS message

        Args:
            phone: Phone number in international format
            message: SMS message content

        Returns:
            Tuple of (success, error_message)
        """
        if not self.initialized:
            # Mock SMS sending in development
            if settings.ENVIRONMENT == "development":
                logger.info(f"MOCK SMS to {phone}: {message}")
                return True, None
            else:
                logger.error("SMS service not initialized - missing credentials")
                return False, "SMS service not configured"

        try:
            # Send SMS using Africa's Talking
            response = self.sms.send(
                message, [phone], sender_id=settings.AFRICAS_TALKING_SENDER_ID
            )

            # Check response
            if response["SMSMessageData"]["Recipients"]:
                recipient = response["SMSMessageData"]["Recipients"][0]
                if recipient["status"] == "Success":
                    logger.info(f"SMS sent successfully to {phone}")
                    return True, None
                else:
                    error_msg = f"SMS failed: {recipient['status']}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                logger.error("No recipients in SMS response")
                return False, "Failed to send SMS"

        except Exception as e:
            error_msg = f"SMS sending error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_otp(self, phone: str, otp: str) -> Tuple[bool, Optional[str]]:
        """
        Send OTP via SMS

        Args:
            phone: Phone number in international format
            otp: OTP code to send

        Returns:
            Tuple of (success, error_message)
        """
        from app.utils.otp_generator import OTPGenerator

        message = OTPGenerator.format_otp_message(otp)
        return self.send_sms(phone, message)

    def send_login_otp(
        self, phone: str, otp: str, first_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send login OTP via SMS

        Args:
            phone: Phone number in international format
            otp: OTP code to send
            first_name: User's first name for personalization

        Returns:
            Tuple of (success, error_message)
        """
        name = first_name if first_name else ""
        greeting = f"Hi {name}, " if name else ""
        message = f"{greeting}Your Matatu Fleet login code is: {otp}. Valid for 5 minutes. Do not share this code."

        return self.send_sms(phone, message)

    def send_welcome_message(
        self, phone: str, first_name: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send welcome message to new user

        Args:
            phone: Phone number in international format
            first_name: User's first name (optional)

        Returns:
            Tuple of (success, error_message)
        """
        name = first_name if first_name else "there"
        message = f"Welcome to Matatu Fleet, {name}! Your account has been created successfully. You can now book trips and track your rides."

        return self.send_sms(phone, message)


# Create global SMS service instance
sms_service = SMSService()
