"""
Tests for OTP generation and validation utilities
"""

import pytest
from datetime import datetime, timedelta
from app.utils.otp_generator import OTPGenerator
from app.core.config import settings

class TestOTPGenerator:
    """Test OTP generation and validation"""
    
    def test_generate_otp_length(self):
        """Test OTP generation length"""
        otp = OTPGenerator.generate_otp()
        assert len(otp) == settings.OTP_LENGTH
        assert otp.isdigit()
    
    def test_generate_otp_uniqueness(self):
        """Test OTP uniqueness"""
        otp1 = OTPGenerator.generate_otp()
        otp2 = OTPGenerator.generate_otp()
        # While not guaranteed, very unlikely to be the same
        assert otp1 != otp2 or len(set([OTPGenerator.generate_otp() for _ in range(10)])) > 1
    
    def test_create_otp_hash(self):
        """Test OTP hash creation"""
        phone = "+254712345678"
        otp = "123456"
        hash1 = OTPGenerator.create_otp_hash(phone, otp)
        hash2 = OTPGenerator.create_otp_hash(phone, otp)
        
        assert hash1 == hash2  # Same input should produce same hash
        assert len(hash1) == 64  # SHA256 hex length
    
    def test_verify_otp_hash_valid(self):
        """Test OTP hash verification with valid OTP"""
        phone = "+254712345678"
        otp = "123456"
        hash_value = OTPGenerator.create_otp_hash(phone, otp)
        
        is_valid = OTPGenerator.verify_otp_hash(phone, otp, hash_value)
        assert is_valid is True
    
    def test_verify_otp_hash_invalid(self):
        """Test OTP hash verification with invalid OTP"""
        phone = "+254712345678"
        otp = "123456"
        wrong_otp = "654321"
        hash_value = OTPGenerator.create_otp_hash(phone, otp)
        
        is_valid = OTPGenerator.verify_otp_hash(phone, wrong_otp, hash_value)
        assert is_valid is False
    
    def test_get_otp_expiry(self):
        """Test OTP expiry calculation"""
        before = datetime.utcnow()
        expiry = OTPGenerator.get_otp_expiry()
        after = datetime.utcnow()
        
        expected_min = before + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        expected_max = after + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        assert expected_min <= expiry <= expected_max
    
    def test_is_otp_expired_false(self):
        """Test OTP expiry check for non-expired OTP"""
        created_at = datetime.utcnow() - timedelta(minutes=1)  # 1 minute ago
        is_expired = OTPGenerator.is_otp_expired(created_at)
        assert is_expired is False
    
    def test_is_otp_expired_true(self):
        """Test OTP expiry check for expired OTP"""
        created_at = datetime.utcnow() - timedelta(minutes=settings.OTP_EXPIRE_MINUTES + 1)
        is_expired = OTPGenerator.is_otp_expired(created_at)
        assert is_expired is True
    
    def test_format_otp_message(self):
        """Test OTP message formatting"""
        otp = "123456"
        message = OTPGenerator.format_otp_message(otp)
        
        assert otp in message
        assert "Matatu Fleet" in message
        assert str(settings.OTP_EXPIRE_MINUTES) in message
        assert "Do not share" in message
