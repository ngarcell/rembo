"""
Admin endpoints for manager account management
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.middleware.auth_middleware import require_admin
from app.models.user_profile import UserProfile, UserRole
from app.services.admin_service import AdminService
from app.utils.phone_validator import PhoneValidator

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize admin service
admin_service = AdminService()


# Request/Response Models
class CreateManagerRequest(BaseModel):
    """Request model for creating a new manager"""

    phone: str = Field(..., description="Manager's phone number")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    fleet_name: Optional[str] = Field(None, max_length=200, description="Fleet to assign manager to")


class ManagerResponse(BaseModel):
    """Response model for manager information"""

    user_id: UUID
    phone: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    fleet_name: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None

    class Config:
        from_attributes = True


class CreateManagerResponse(BaseModel):
    """Response model for manager creation"""

    success: bool
    message: str
    manager: ManagerResponse
    temporary_access_code: str


class ManagerListResponse(BaseModel):
    """Response model for manager list"""

    managers: List[ManagerResponse]
    total_count: int


class FleetAssignmentRequest(BaseModel):
    """Request model for fleet assignment"""

    fleet_name: str = Field(..., max_length=200)


class AdminActionResponse(BaseModel):
    """Response model for admin actions"""

    success: bool
    message: str


# Admin Endpoints
@router.post(
    "/managers",
    response_model=CreateManagerResponse,
    summary="Create new manager account",
    description="Create a new manager account with temporary access credentials",
)
def create_manager(
    request: CreateManagerRequest,
    db: Session = Depends(get_db),
    admin_user: UserProfile = Depends(require_admin),
):
    """
    Create a new manager account (Admin only)

    Args:
        request: Manager creation request
        db: Database session
        admin_user: Current admin user

    Returns:
        CreateManagerResponse: Manager creation result with temporary credentials
    """
    try:
        # Validate phone number
        is_valid, phone, error_msg = PhoneValidator.validate_phone(request.phone)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        # Create manager
        success, response_data = admin_service.create_manager(
            phone=phone,
            first_name=request.first_name,
            last_name=request.last_name,
            fleet_name=request.fleet_name,
            created_by_admin_id=str(admin_user.user_id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")
            
            if error_code == "PHONE_EXISTS":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_data["message"],
                )
            elif error_code == "FLEET_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return CreateManagerResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manager creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manager creation failed",
        )


@router.get(
    "/managers",
    response_model=ManagerListResponse,
    summary="List all managers",
    description="Get list of all manager accounts",
)
def list_managers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    admin_user: UserProfile = Depends(require_admin),
):
    """
    List all manager accounts (Admin only)

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter for active managers only
        db: Database session
        admin_user: Current admin user

    Returns:
        ManagerListResponse: List of managers
    """
    try:
        success, response_data = admin_service.list_managers(
            skip=skip,
            limit=limit,
            active_only=active_only,
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_data.get("message", "Failed to retrieve managers"),
            )

        return ManagerListResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manager list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve managers",
        )


@router.get(
    "/managers/{manager_id}",
    response_model=ManagerResponse,
    summary="Get manager details",
    description="Get detailed information about a specific manager",
)
def get_manager(
    manager_id: UUID,
    db: Session = Depends(get_db),
    admin_user: UserProfile = Depends(require_admin),
):
    """
    Get manager details (Admin only)

    Args:
        manager_id: Manager's user ID
        db: Database session
        admin_user: Current admin user

    Returns:
        ManagerResponse: Manager details
    """
    try:
        success, response_data = admin_service.get_manager(
            manager_id=str(manager_id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")
            
            if error_code == "MANAGER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return ManagerResponse(**response_data["manager"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get manager error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve manager",
        )


@router.post(
    "/managers/{manager_id}/activate",
    response_model=AdminActionResponse,
    summary="Activate manager account",
    description="Activate a deactivated manager account",
)
def activate_manager(
    manager_id: UUID,
    db: Session = Depends(get_db),
    admin_user: UserProfile = Depends(require_admin),
):
    """
    Activate manager account (Admin only)

    Args:
        manager_id: Manager's user ID
        db: Database session
        admin_user: Current admin user

    Returns:
        AdminActionResponse: Action result
    """
    try:
        success, response_data = admin_service.activate_manager(
            manager_id=str(manager_id),
            admin_id=str(admin_user.user_id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")
            
            if error_code == "MANAGER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return AdminActionResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manager activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manager activation failed",
        )


@router.post(
    "/managers/{manager_id}/deactivate",
    response_model=AdminActionResponse,
    summary="Deactivate manager account",
    description="Deactivate a manager account",
)
def deactivate_manager(
    manager_id: UUID,
    db: Session = Depends(get_db),
    admin_user: UserProfile = Depends(require_admin),
):
    """
    Deactivate manager account (Admin only)

    Args:
        manager_id: Manager's user ID
        db: Database session
        admin_user: Current admin user

    Returns:
        AdminActionResponse: Action result
    """
    try:
        success, response_data = admin_service.deactivate_manager(
            manager_id=str(manager_id),
            admin_id=str(admin_user.user_id),
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")
            
            if error_code == "MANAGER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return AdminActionResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manager deactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manager deactivation failed",
        )
