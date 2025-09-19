"""
Tests for phone number validation utilities
"""

import pytest
from app.utils.phone_validator import PhoneValidator


class TestPhoneValidator:
    """Test phone number validation"""

    def test_normalize_phone_with_plus_254(self):
        """Test normalization with +254 prefix"""
        phone = "+254712345678"
        result = PhoneValidator.normalize_phone(phone)
        assert result == "+254712345678"

    def test_normalize_phone_with_254(self):
        """Test normalization with 254 prefix"""
        phone = "254712345678"
        result = PhoneValidator.normalize_phone(phone)
        assert result == "+254712345678"

    def test_normalize_phone_with_zero(self):
        """Test normalization with 0 prefix"""
        phone = "0712345678"
        result = PhoneValidator.normalize_phone(phone)
        assert result == "+254712345678"

    def test_normalize_phone_without_prefix(self):
        """Test normalization without prefix"""
        phone = "712345678"
        result = PhoneValidator.normalize_phone(phone)
        assert result == "+254712345678"

    def test_validate_valid_safaricom_number(self):
        """Test validation of valid Safaricom number"""
        phone = "+254712345678"
        is_valid, normalized, error = PhoneValidator.validate_phone(phone)
        assert is_valid is True
        assert normalized == "+254712345678"
        assert error is None

    def test_validate_valid_airtel_number(self):
        """Test validation of valid Airtel number"""
        phone = "+254732345678"
        is_valid, normalized, error = PhoneValidator.validate_phone(phone)
        assert is_valid is True
        assert normalized == "+254732345678"
        assert error is None

    def test_validate_invalid_length(self):
        """Test validation of invalid length"""
        phone = "+25471234567"  # Too short
        is_valid, normalized, error = PhoneValidator.validate_phone(phone)
        assert is_valid is False
        assert normalized is None
        assert "13 digits" in error

    def test_validate_invalid_format(self):
        """Test validation of invalid format"""
        phone = "+254812345678"  # Invalid prefix
        is_valid, normalized, error = PhoneValidator.validate_phone(phone)
        assert is_valid is False
        assert normalized is None
        assert "Invalid Kenyan phone number" in error

    def test_validate_empty_phone(self):
        """Test validation of empty phone"""
        phone = ""
        is_valid, normalized, error = PhoneValidator.validate_phone(phone)
        assert is_valid is False
        assert normalized is None
        assert "required" in error

    def test_format_for_display(self):
        """Test display formatting"""
        phone = "+254712345678"
        result = PhoneValidator.format_for_display(phone)
        assert result == "+254 712 345 678"

    def test_format_for_sms(self):
        """Test SMS formatting"""
        phone = "0712345678"
        result = PhoneValidator.format_for_sms(phone)
        assert result == "+254712345678"
