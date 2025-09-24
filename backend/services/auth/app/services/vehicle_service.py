"""
Vehicle Service for managing fleet vehicles
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime

from app.models.simple_vehicle import SimpleVehicle, VehicleStatus
from app.models.fleet import Fleet
from app.models.user_profile import UserProfile
from app.schemas.vehicle import VehicleRegistrationRequest, VehicleUpdateRequest
from app.core.encryption import encrypt_sensitive_data, decrypt_sensitive_data

logger = logging.getLogger(__name__)


class VehicleService:
    """Service for managing vehicles"""

    @staticmethod
    def register_vehicle(
        vehicle_data: VehicleRegistrationRequest,
        manager_id: str,
        fleet_id: str,
        db: Session,
    ) -> Tuple[bool, Optional[SimpleVehicle], Optional[str]]:
        """
        Register a new vehicle

        Args:
            vehicle_data: Vehicle registration data
            manager_id: Manager registering the vehicle
            fleet_id: Fleet ID where vehicle belongs
            db: Database session

        Returns:
            Tuple of (success, vehicle, error_message)
        """
        try:
            # Verify manager has access to this fleet
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(
                        UserProfile.id == manager_id,
                        UserProfile.fleet_id == fleet_id,
                        UserProfile.role == "manager",
                    )
                )
                .first()
            )

            if not manager:
                return False, None, "Manager not authorized for this fleet"

            # Check license plate uniqueness
            existing_vehicle = (
                db.query(SimpleVehicle)
                .filter(SimpleVehicle.license_plate == vehicle_data.license_plate)
                .first()
            )

            if existing_vehicle:
                return (
                    False,
                    None,
                    f"License plate {vehicle_data.license_plate} already exists",
                )

            # Check fleet number uniqueness within fleet
            existing_fleet_number = (
                db.query(SimpleVehicle)
                .filter(
                    and_(
                        SimpleVehicle.fleet_id == fleet_id,
                        SimpleVehicle.fleet_number == vehicle_data.fleet_number,
                    )
                )
                .first()
            )

            if existing_fleet_number:
                return (
                    False,
                    None,
                    f"Fleet number {vehicle_data.fleet_number} already exists in this fleet",
                )

            # Encrypt GPS API key if provided
            encrypted_api_key = None
            if vehicle_data.gps_api_key:
                encrypted_api_key = encrypt_sensitive_data(vehicle_data.gps_api_key)

            # Create vehicle with simplified fields
            vehicle = SimpleVehicle(
                fleet_id=fleet_id,
                manager_id=manager_id,
                fleet_number=vehicle_data.fleet_number,
                license_plate=vehicle_data.license_plate,
                capacity=vehicle_data.capacity,
                route=vehicle_data.route,
                gps_device_id=vehicle_data.gps_device_id,
                sim_number=vehicle_data.sim_number,
                gps_api_key=encrypted_api_key,
                status=VehicleStatus.ACTIVE,
                is_active=True,
            )

            db.add(vehicle)
            db.commit()
            db.refresh(vehicle)

            logger.info(
                f"Vehicle registered: {vehicle.license_plate} by manager {manager_id}"
            )
            return True, vehicle, None

        except Exception as e:
            db.rollback()
            logger.error(f"Vehicle registration error: {e}")
            return False, None, "Vehicle registration failed"

    @staticmethod
    def get_fleet_vehicles(
        fleet_id: str,
        manager_id: str,
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        vehicle_type: Optional[str] = None,
    ) -> Tuple[List[SimpleVehicle], int]:
        """
        Get vehicles for a fleet with filtering and pagination

        Args:
            fleet_id: Fleet ID
            manager_id: Manager ID (for access control)
            db: Database session
            page: Page number
            limit: Items per page
            search: Search term
            status: Filter by status
            vehicle_type: Filter by vehicle type

        Returns:
            Tuple of (vehicles, total_count)
        """
        try:
            # Verify manager has access to this fleet
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(
                        UserProfile.id == manager_id,
                        UserProfile.fleet_id == fleet_id,
                        UserProfile.role == "manager",
                    )
                )
                .first()
            )

            if not manager:
                return [], 0

            # Build query
            query = db.query(SimpleVehicle).filter(SimpleVehicle.fleet_id == fleet_id)

            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SimpleVehicle.license_plate.ilike(search_term),
                        SimpleVehicle.fleet_number.ilike(search_term),
                        SimpleVehicle.make.ilike(search_term),
                        SimpleVehicle.model.ilike(search_term),
                        SimpleVehicle.route.ilike(search_term),
                    )
                )

            if status:
                query = query.filter(SimpleVehicle.status == status)

            if vehicle_type:
                query = query.filter(SimpleVehicle.vehicle_type == vehicle_type)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            vehicles = (
                query.order_by(SimpleVehicle.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            return vehicles, total_count

        except Exception as e:
            logger.error(f"Error getting fleet vehicles: {e}")
            return [], 0

    @staticmethod
    def get_vehicle_by_id(
        vehicle_id: str, manager_id: str, db: Session
    ) -> Optional[SimpleVehicle]:
        """
        Get vehicle by ID with access control

        Args:
            vehicle_id: Vehicle ID
            manager_id: Manager ID (for access control)
            db: Database session

        Returns:
            Vehicle or None
        """
        try:
            # Get vehicle with fleet access check
            vehicle = (
                db.query(SimpleVehicle)
                .join(UserProfile, SimpleVehicle.fleet_id == UserProfile.fleet_id)
                .filter(
                    and_(
                        SimpleVehicle.id == vehicle_id,
                        UserProfile.id == manager_id,
                        UserProfile.role == "manager",
                    )
                )
                .first()
            )

            return vehicle

        except Exception as e:
            logger.error(f"Error getting vehicle by ID: {e}")
            return None

    @staticmethod
    def update_vehicle(
        vehicle_id: str,
        vehicle_data: VehicleUpdateRequest,
        manager_id: str,
        db: Session,
    ) -> Tuple[bool, Optional[SimpleVehicle], Optional[str]]:
        """
        Update vehicle information

        Args:
            vehicle_id: Vehicle ID
            vehicle_data: Updated vehicle data
            manager_id: Manager updating the vehicle
            db: Database session

        Returns:
            Tuple of (success, vehicle, error_message)
        """
        try:
            # Get vehicle with access control
            vehicle = VehicleService.get_vehicle_by_id(vehicle_id, manager_id, db)
            if not vehicle:
                return False, None, "Vehicle not found or access denied"

            # Check license plate uniqueness if being updated
            if (
                vehicle_data.license_plate
                and vehicle_data.license_plate != vehicle.license_plate
            ):
                existing_vehicle = (
                    db.query(SimpleVehicle)
                    .filter(
                        and_(
                            SimpleVehicle.license_plate == vehicle_data.license_plate,
                            SimpleVehicle.id != vehicle_id,
                        )
                    )
                    .first()
                )

                if existing_vehicle:
                    return (
                        False,
                        None,
                        f"License plate {vehicle_data.license_plate} already exists",
                    )

            # Check fleet number uniqueness if being updated
            if (
                vehicle_data.fleet_number
                and vehicle_data.fleet_number != vehicle.fleet_number
            ):
                existing_fleet_number = (
                    db.query(SimpleVehicle)
                    .filter(
                        and_(
                            SimpleVehicle.fleet_id == vehicle.fleet_id,
                            SimpleVehicle.fleet_number == vehicle_data.fleet_number,
                            SimpleVehicle.id != vehicle_id,
                        )
                    )
                    .first()
                )

                if existing_fleet_number:
                    return (
                        False,
                        None,
                        f"Fleet number {vehicle_data.fleet_number} already exists in this fleet",
                    )

            # Update fields
            update_data = vehicle_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(vehicle, field):
                    setattr(vehicle, field, value)

            vehicle.updated_at = datetime.utcnow()

            # Update compliance status
            vehicle.update_status_based_on_compliance()

            db.commit()
            db.refresh(vehicle)

            logger.info(
                f"Vehicle updated: {vehicle.license_plate} by manager {manager_id}"
            )
            return True, vehicle, None

        except Exception as e:
            db.rollback()
            logger.error(f"Vehicle update error: {e}")
            return False, None, "Vehicle update failed"

    @staticmethod
    def get_fleet_name(fleet_id: str, db: Session) -> Optional[str]:
        """Get fleet name by ID"""
        try:
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            return fleet.name if fleet else None
        except Exception as e:
            logger.error(f"Error getting fleet name: {e}")
            return None
