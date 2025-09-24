"""
Manager endpoints for driver registration and management
"""

import logging
from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager
from app.models.user_profile import UserProfile
from app.services.driver_service import driver_service
from app.utils.phone_validator import PhoneValidator

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class RegisterDriverRequest(BaseModel):
    """Request model for driver registration"""

    first_name: str = Field(
        ..., min_length=1, max_length=100, description="Driver's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Driver's last name"
    )
    phone: str = Field(..., description="Driver's phone number")
    email: Optional[str] = Field(
        None, max_length=255, description="Driver's email address"
    )
    date_of_birth: Optional[date] = Field(None, description="Driver's date of birth")
    national_id: Optional[str] = Field(
        None, max_length=50, description="Driver's national ID"
    )
    license_number: str = Field(
        ..., min_length=1, max_length=50, description="Driver's license number"
    )
    license_class: str = Field(
        ..., min_length=1, max_length=10, description="Driver's license class"
    )
    license_expiry: date = Field(..., description="License expiry date")
    hire_date: Optional[date] = Field(None, description="Hire date (defaults to today)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        is_valid, normalized, error = PhoneValidator.validate_phone(v)
        if not is_valid:
            raise ValueError(f"Invalid phone number: {error}")
        return normalized

    @field_validator("license_expiry", "hire_date")
    @classmethod
    def validate_dates(cls, v, info):
        """Validate dates are not in the past"""
        if v and info.field_name == "license_expiry" and v < date.today():
            raise ValueError("License expiry date cannot be in the past")
        return v


class DriverResponse(BaseModel):
    """Response model for driver information"""

    id: str
    driver_id: str
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_id: Optional[str] = None
    license_number: str
    license_class: str
    license_expiry: str
    hire_date: str
    employment_status: str
    is_active: bool
    fleet_id: str
    manager_id: str
    created_at: str
    updated_at: str


class RegisterDriverResponse(BaseModel):
    """Response model for driver registration"""

    success: bool
    message: str
    driver: DriverResponse
    fleet_name: str


class DriverListResponse(BaseModel):
    """Response model for driver list"""

    drivers: List[DriverResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class DriverDetailsResponse(BaseModel):
    """Response model for driver details"""

    driver: DriverResponse
    fleet_name: Optional[str] = None


# Manager Endpoints
@router.post(
    "/drivers",
    response_model=RegisterDriverResponse,
    summary="Register new driver",
    description="Register a new driver in the manager's fleet",
)
def register_driver(
    request: RegisterDriverRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Register a new driver (Manager only)

    Args:
        request: Driver registration request
        db: Database session
        manager: Current manager user

    Returns:
        RegisterDriverResponse: Registration result with driver details
    """
    try:
        # Register driver
        success, response_data = driver_service.register_driver(
            manager_id=str(manager.user_id),
            fleet_id=str(manager.fleet_id),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            email=request.email,
            date_of_birth=request.date_of_birth,
            national_id=request.national_id,
            license_number=request.license_number,
            license_class=request.license_class,
            license_expiry=request.license_expiry,
            hire_date=request.hire_date,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code in ["PHONE_EXISTS", "LICENSE_EXISTS"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=response_data["message"],
                )
            elif error_code in ["FLEET_NOT_FOUND", "FLEET_ACCESS_DENIED"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response_data["message"],
                )
            elif error_code == "DRIVER_ID_GENERATION_FAILED":
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return RegisterDriverResponse(
            success=True,
            message=response_data["message"],
            driver=DriverResponse(**response_data["driver"]),
            fleet_name=response_data["fleet_name"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Driver registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Driver registration failed",
        )


@router.get(
    "/drivers",
    response_model=DriverListResponse,
    summary="List fleet drivers",
    description="Get list of drivers in the manager's fleet",
)
def list_drivers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Filter by employment status"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    List drivers in manager's fleet

    Args:
        page: Page number (1-based)
        limit: Items per page
        search: Search term for name, phone, or driver ID
        status: Filter by employment status
        db: Database session
        manager: Current manager user

    Returns:
        DriverListResponse: List of drivers with pagination
    """
    try:
        success, response_data = driver_service.get_fleet_drivers(
            manager_id=str(manager.user_id),
            fleet_id=str(manager.fleet_id),
            page=page,
            limit=limit,
            search=search,
            status_filter=status,
            db=db,
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "ACCESS_DENIED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        return DriverListResponse(
            drivers=[DriverResponse(**driver) for driver in response_data["drivers"]],
            total_count=response_data["total_count"],
            page=response_data["page"],
            limit=response_data["limit"],
            total_pages=response_data["total_pages"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List drivers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve drivers",
        )


@router.get(
    "/drivers/{driver_id}",
    response_model=DriverDetailsResponse,
    summary="Get driver details",
    description="Get detailed information about a specific driver",
)
def get_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get driver details (Manager only)

    Args:
        driver_id: Driver's UUID
        db: Database session
        manager: Current manager user

    Returns:
        DriverDetailsResponse: Driver details
    """
    try:
        success, response_data = driver_service.get_driver_details(
            manager_id=str(manager.user_id), driver_id=str(driver_id), db=db
        )

        if not success:
            error_code = response_data.get("error_code", "UNKNOWN_ERROR")

            if error_code == "DRIVER_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_data["message"],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data["message"],
                )

        driver_data = response_data["driver"]
        return DriverDetailsResponse(
            driver=DriverResponse(**driver_data),
            fleet_name=driver_data.get("fleet_name"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get driver details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve driver details",
        )
