"""
Driver Registration and Management Service
"""

import logging
import uuid
from datetime import datetime, date
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.simple_driver import SimpleDriver
from app.models.user_profile import UserProfile, UserRole
from app.models.fleet import Fleet
from app.services.driver_id_service import DriverIDService
from app.utils.phone_validator import PhoneValidator

logger = logging.getLogger(__name__)


class DriverService:
    """Service for driver registration and management"""

    def __init__(self):
        """Initialize driver service"""
        self.driver_id_service = DriverIDService()
        logger.info("Driver service initialized")

    def register_driver(
        self,
        manager_id: str,
        fleet_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        license_number: str,
        license_class: str,
        license_expiry: date,
        email: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        national_id: Optional[str] = None,
        hire_date: Optional[date] = None,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Register a new driver

        Args:
            manager_id: Manager's user ID
            fleet_id: Fleet ID to assign driver to
            first_name: Driver's first name
            last_name: Driver's last name
            phone: Driver's phone number
            license_number: Driver's license number
            license_class: Driver's license class
            license_expiry: License expiry date
            email: Driver's email (optional)
            date_of_birth: Driver's date of birth (optional)
            national_id: Driver's national ID (optional)
            hire_date: Hire date (optional, defaults to today)
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Validate manager exists and has access to fleet
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(
                        UserProfile.user_id == manager_id,
                        UserProfile.role == UserRole.MANAGER,
                        UserProfile.is_active == True,
                    )
                )
                .first()
            )

            if not manager:
                return False, {
                    "message": "Manager not found or inactive",
                    "error_code": "MANAGER_NOT_FOUND",
                }

            # Validate fleet exists and manager has access
            fleet = (
                db.query(Fleet)
                .filter(and_(Fleet.id == fleet_id, Fleet.is_active == True))
                .first()
            )

            if not fleet:
                return False, {
                    "message": "Fleet not found or inactive",
                    "error_code": "FLEET_NOT_FOUND",
                }

            # Check if manager is assigned to this fleet
            if manager.fleet_id != fleet.id:
                return False, {
                    "message": "Manager does not have access to this fleet",
                    "error_code": "FLEET_ACCESS_DENIED",
                }

            # Validate and format phone number
            is_valid, phone, error = PhoneValidator.validate_phone(phone)
            if not is_valid:
                return False, {
                    "message": f"Invalid phone number: {error}",
                    "error_code": "INVALID_PHONE",
                }

            # Check if phone number is already registered
            existing_driver = (
                db.query(SimpleDriver).filter(SimpleDriver.phone == phone).first()
            )

            if existing_driver:
                return False, {
                    "message": "Phone number already registered to another driver",
                    "error_code": "PHONE_EXISTS",
                }

            # Check if license number is already registered
            existing_license = (
                db.query(SimpleDriver)
                .filter(SimpleDriver.license_number == license_number)
                .first()
            )

            if existing_license:
                return False, {
                    "message": "License number already registered to another driver",
                    "error_code": "LICENSE_EXISTS",
                }

            # Generate unique driver ID
            success, driver_id, error = self.driver_id_service.generate_driver_id(
                fleet_id, db
            )
            if not success:
                return False, {
                    "message": error or "Failed to generate driver ID",
                    "error_code": "DRIVER_ID_GENERATION_FAILED",
                }

            # Create driver profile
            driver = SimpleDriver(
                driver_code=driver_id,
                fleet_id=fleet_id,
                license_number=license_number,
                license_expiry=license_expiry,
                is_active=True,
            )

            db.add(driver)
            db.commit()
            db.refresh(driver)

            logger.info(
                f"Driver registered successfully: {driver_id} by manager {manager_id}"
            )

            return True, {
                "message": "Driver registered successfully",
                "driver": driver.to_dict(),
                "fleet_name": fleet.name,
            }

        except Exception as e:
            logger.error(f"Driver registration error: {e}")
            db.rollback()
            return False, {
                "message": "Driver registration failed. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }

    def get_fleet_drivers(
        self,
        manager_id: str,
        fleet_id: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get drivers for a fleet (manager access only)

        Args:
            manager_id: Manager's user ID
            fleet_id: Fleet ID
            page: Page number (1-based)
            limit: Items per page
            search: Search term for name, phone, or driver ID
            status_filter: Filter by employment status
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Validate manager access
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(
                        UserProfile.user_id == manager_id,
                        UserProfile.role == UserRole.MANAGER,
                        UserProfile.is_active == True,
                        UserProfile.fleet_id == fleet_id,
                    )
                )
                .first()
            )

            if not manager:
                return False, {
                    "message": "Manager not found or no access to fleet",
                    "error_code": "ACCESS_DENIED",
                }

            # Build query
            query = db.query(SimpleDriver).filter(SimpleDriver.fleet_id == fleet_id)

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SimpleDriver.first_name.ilike(search_term),
                        SimpleDriver.last_name.ilike(search_term),
                        SimpleDriver.phone.ilike(search_term),
                        SimpleDriver.driver_id.ilike(search_term),
                        SimpleDriver.license_number.ilike(search_term),
                    )
                )

            # Apply status filter
            if status_filter:
                query = query.filter(SimpleDriver.employment_status == status_filter)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            drivers = query.offset(offset).limit(limit).all()

            # Convert to dict
            drivers_data = [driver.to_dict() for driver in drivers]

            return True, {
                "drivers": drivers_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit,
            }

        except Exception as e:
            logger.error(f"Get fleet drivers error: {e}")
            return False, {
                "message": "Failed to retrieve drivers",
                "error_code": "INTERNAL_ERROR",
            }

    def get_driver_details(
        self, manager_id: str, driver_id: str, db: Session = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get driver details (manager access only)

        Args:
            manager_id: Manager's user ID
            driver_id: Driver's UUID
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get driver with fleet access validation
            driver = (
                db.query(SimpleDriver)
                .join(UserProfile, UserProfile.id == SimpleDriver.manager_id)
                .filter(
                    and_(
                        SimpleDriver.id == driver_id,
                        UserProfile.user_id == manager_id,
                        UserProfile.role == UserRole.MANAGER,
                        UserProfile.is_active == True,
                    )
                )
                .first()
            )

            if not driver:
                return False, {
                    "message": "Driver not found or access denied",
                    "error_code": "DRIVER_NOT_FOUND",
                }

            # Get fleet information
            fleet = db.query(Fleet).filter(Fleet.id == driver.fleet_id).first()

            driver_data = driver.to_dict()
            driver_data["fleet_name"] = fleet.name if fleet else None

            return True, {"driver": driver_data}

        except Exception as e:
            logger.error(f"Get driver details error: {e}")
            return False, {
                "message": "Failed to retrieve driver details",
                "error_code": "INTERNAL_ERROR",
            }


# Global driver service instance
driver_service = DriverService()
