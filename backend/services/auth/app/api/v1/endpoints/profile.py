"""
User profile endpoints (protected routes)
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user_profile import UserProfile
from app.utils.phone_validator import PhoneValidator

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class UserProfileResponse(BaseModel):
    """User profile response model"""

    id: str
    user_id: str
    phone: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: str
    updated_at: str


class UpdateProfileRequest(BaseModel):
    """Request model for profile updates"""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UpdateProfileResponse(BaseModel):
    """Response model for profile updates"""

    message: str
    user: UserProfileResponse


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user",
)
def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """
    Get current user's profile

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    try:
        return UserProfileResponse(
            id=str(current_user.id),
            user_id=str(current_user.user_id),
            phone=PhoneValidator.format_for_display(current_user.phone),
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            role=current_user.role.value,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        )


@router.put(
    "/profile",
    response_model=UpdateProfileResponse,
    summary="Update user profile",
    description="Update the current user's profile information",
)
def update_user_profile(
    request: UpdateProfileRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile

    Args:
        request: Profile update request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated profile data

    Raises:
        HTTPException: If profile update fails
    """
    try:
        # Update fields if provided
        updated = False

        if request.first_name is not None:
            current_user.first_name = request.first_name.strip()
            updated = True

        if request.last_name is not None:
            current_user.last_name = request.last_name.strip()
            updated = True

        if request.email is not None:
            current_user.email = request.email
            updated = True

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        # Save changes
        db.commit()
        db.refresh(current_user)

        logger.info(f"Profile updated for user: {current_user.id}")

        return UpdateProfileResponse(
            message="Profile updated successfully",
            user=UserProfileResponse(
                id=str(current_user.id),
                user_id=str(current_user.user_id),
                phone=PhoneValidator.format_for_display(current_user.phone),
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                email=current_user.email,
                role=current_user.role.value,
                is_active=current_user.is_active,
                created_at=current_user.created_at.isoformat(),
                updated_at=current_user.updated_at.isoformat(),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@router.get(
    "/dashboard",
    summary="Get user dashboard data",
    description="Get dashboard data for the current user",
)
def get_user_dashboard(current_user: UserProfile = Depends(get_current_user)):
    """
    Get user dashboard data

    Args:
        current_user: Current authenticated user

    Returns:
        Dashboard data based on user role
    """
    try:
        dashboard_data = {
            "user": {
                "id": str(current_user.id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "role": current_user.role.value,
                "phone": PhoneValidator.format_for_display(current_user.phone),
            },
            "stats": {},
            "recent_activity": [],
            "notifications": [],
        }

        # Role-specific dashboard data
        if current_user.role.value == "passenger":
            dashboard_data["stats"] = {
                "total_trips": 0,
                "completed_trips": 0,
                "cancelled_trips": 0,
                "total_spent": 0,
            }
            dashboard_data["quick_actions"] = [
                {"title": "Book a Trip", "action": "book_trip"},
                {"title": "Trip History", "action": "view_history"},
                {"title": "Favorite Routes", "action": "view_favorites"},
            ]

        elif current_user.role.value == "admin":
            dashboard_data["stats"] = {
                "total_users": 0,
                "active_drivers": 0,
                "total_fleets": 0,
                "system_health": "good",
            }
            dashboard_data["quick_actions"] = [
                {"title": "Manage Users", "action": "manage_users"},
                {"title": "Fleet Overview", "action": "fleet_overview"},
                {"title": "System Reports", "action": "system_reports"},
            ]

        elif current_user.role.value == "manager":
            dashboard_data["stats"] = {
                "fleet_drivers": 0,
                "active_vehicles": 0,
                "daily_revenue": 0,
                "pending_approvals": 0,
            }
            dashboard_data["quick_actions"] = [
                {"title": "Manage Drivers", "action": "manage_drivers"},
                {"title": "Vehicle Status", "action": "vehicle_status"},
                {"title": "Revenue Reports", "action": "revenue_reports"},
            ]

        return dashboard_data

    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )
