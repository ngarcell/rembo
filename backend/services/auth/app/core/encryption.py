"""
Encryption utilities for sensitive data
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""

    def __init__(self):
        self._key = None
        self._fernet = None
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption with key from environment"""
        try:
            # Get encryption key from environment or generate one
            encryption_key = os.getenv("ENCRYPTION_KEY")

            if not encryption_key:
                # Generate a key for development (not recommended for production)
                logger.warning(
                    "No ENCRYPTION_KEY found in environment. Generating temporary key."
                )
                encryption_key = Fernet.generate_key().decode()
                logger.warning(f"Generated encryption key: {encryption_key}")
                logger.warning(
                    "Please set ENCRYPTION_KEY environment variable for production"
                )

            # If the key is a string, encode it
            if isinstance(encryption_key, str):
                # Try to decode as base64 first
                try:
                    key_bytes = base64.urlsafe_b64decode(encryption_key.encode())
                    if len(key_bytes) == 32:  # Fernet key should be 32 bytes
                        self._key = base64.urlsafe_b64encode(key_bytes)
                    else:
                        raise ValueError("Invalid key length")
                except:
                    # If not valid base64, derive key from password
                    self._key = self._derive_key_from_password(encryption_key)
            else:
                self._key = encryption_key

            self._fernet = Fernet(self._key)
            logger.info("Encryption service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to a default key for development
            self._key = Fernet.generate_key()
            self._fernet = Fernet(self._key)
            logger.warning("Using fallback encryption key")

    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password"""
        # Use a fixed salt for consistency (not recommended for production)
        salt = b"matatu_fleet_salt_2025"  # Should be random and stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            if not data:
                return data

            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return data  # Return original data if encryption fails

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            if not encrypted_data:
                return encrypted_data

            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()

        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_data  # Return original data if decryption fails


# Global encryption service instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return get_encryption_service().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return get_encryption_service().decrypt(encrypted_data)
