"""
JWT Token Service for authentication and authorization
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class JWTService:
    """Service for handling JWT token operations"""

    @staticmethod
    def create_access_token(
        user_id: str,
        phone: str,
        role: str = "passenger",
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token

        Args:
            user_id: User's unique identifier
            phone: User's phone number
            role: User's role (passenger, admin, manager)
            expires_delta: Custom expiration time

        Returns:
            JWT token string
        """
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=settings.JWT_EXPIRE_MINUTES
                )

            payload = {
                "sub": user_id,  # Subject (user ID)
                "phone": phone,
                "role": role,
                "exp": expire,
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4()),  # JWT ID for token tracking
                "type": "access",
            }

            token = jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
            )

            logger.info(f"Access token created for user: {user_id}")
            return token

        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create JWT refresh token

        Args:
            user_id: User's unique identifier

        Returns:
            JWT refresh token string
        """
        try:
            expire = datetime.utcnow() + timedelta(
                days=settings.JWT_REFRESH_EXPIRE_DAYS
            )

            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4()),
                "type": "refresh",
            }

            token = jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
            )

            logger.info(f"Refresh token created for user: {user_id}")
            return token

        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid
            ExpiredSignatureError: If token is expired
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            # Validate required fields
            if not payload.get("sub"):
                raise InvalidTokenError("Token missing subject")

            if not payload.get("type"):
                raise InvalidTokenError("Token missing type")

            logger.debug(f"Token verified for user: {payload.get('sub')}")
            return payload

        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise InvalidTokenError("Token verification failed")

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """
        Create new access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary with new access token and refresh token

        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = JWTService.verify_token(refresh_token)

            if payload.get("type") != "refresh":
                raise InvalidTokenError("Invalid token type for refresh")

            user_id = payload.get("sub")

            # Create new tokens
            new_access_token = JWTService.create_access_token(
                user_id=user_id,
                phone="",  # We'll need to get this from database
                role="passenger",  # We'll need to get this from database
            )

            new_refresh_token = JWTService.create_refresh_token(user_id)

            logger.info(f"Tokens refreshed for user: {user_id}")

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    @staticmethod
    def get_user_from_token(token: str) -> Optional[str]:
        """
        Extract user ID from token without full verification

        Args:
            token: JWT token string

        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = JWTService.verify_token(token)
            return payload.get("sub")
        except Exception:
            return None

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Check if token is expired without raising exception

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        try:
            JWTService.verify_token(token)
            return False
        except ExpiredSignatureError:
            return True
        except Exception:
            return True


# Create global JWT service instance
jwt_service = JWTService()
