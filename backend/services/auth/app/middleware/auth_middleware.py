"""
Authentication middleware for protecting routes
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.jwt_service import jwt_service
from app.models.user_profile import UserProfile
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware class"""
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> UserProfile:
        """
        Get current authenticated user from JWT token
        
        Args:
            credentials: HTTP Bearer credentials
            db: Database session
            
        Returns:
            UserProfile: Current user profile
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Extract token
            token = credentials.credentials
            
            # Verify token
            payload = jwt_service.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Get user from database
            user = db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.debug(f"User authenticated: {user.id}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_current_active_user(
        current_user: UserProfile = Depends(get_current_user)
    ) -> UserProfile:
        """
        Get current active user (alias for get_current_user)
        
        Args:
            current_user: Current user from get_current_user
            
        Returns:
            UserProfile: Current active user
        """
        return current_user
    
    @staticmethod
    def require_role(required_role: str):
        """
        Create dependency that requires specific user role
        
        Args:
            required_role: Required user role (admin, manager, passenger)
            
        Returns:
            Dependency function
        """
        def role_checker(
            current_user: UserProfile = Depends(AuthMiddleware.get_current_user)
        ) -> UserProfile:
            if current_user.role.value != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation requires {required_role} role"
                )
            return current_user
        
        return role_checker
    
    @staticmethod
    def require_admin(
        current_user: UserProfile = Depends(get_current_user)
    ) -> UserProfile:
        """
        Require admin role
        
        Args:
            current_user: Current user
            
        Returns:
            UserProfile: Admin user
            
        Raises:
            HTTPException: If user is not admin
        """
        if current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    @staticmethod
    def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
        db: Session = Depends(get_db)
    ) -> Optional[UserProfile]:
        """
        Get current user if token is provided, otherwise return None
        
        Args:
            credentials: Optional HTTP Bearer credentials
            db: Database session
            
        Returns:
            UserProfile or None
        """
        if not credentials:
            return None
        
        try:
            return AuthMiddleware.get_current_user(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=credentials.credentials
                ),
                db
            )
        except HTTPException:
            return None


# Create dependency instances
get_current_user = AuthMiddleware.get_current_user
get_current_active_user = AuthMiddleware.get_current_active_user
require_admin = AuthMiddleware.require_admin
get_optional_user = AuthMiddleware.get_optional_user
