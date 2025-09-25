"""
Assignment Service for managing driver-vehicle assignments
"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.vehicle_assignment import VehicleAssignment
from app.models.simple_vehicle import SimpleVehicle
from app.models.simple_driver import SimpleDriver
from app.models.fleet import Fleet
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)


class AssignmentService:
    """Service for managing driver-vehicle assignments"""

    @staticmethod
    def create_assignment(
        driver_id: str,
        vehicle_id: str,
        manager_id: str,
        fleet_id: str,
        assignment_notes: Optional[str],
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new driver-vehicle assignment

        Args:
            driver_id: Driver UUID
            vehicle_id: Vehicle UUID
            manager_id: Manager UUID
            fleet_id: Fleet UUID
            assignment_notes: Optional notes
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Validate driver exists and is active
            driver = (
                db.query(SimpleDriver)
                .filter(
                    SimpleDriver.id == driver_id,
                    SimpleDriver.fleet_id == fleet_id,
                    SimpleDriver.is_active == True,
                )
                .first()
            )

            if not driver:
                return False, {
                    "error_code": "DRIVER_NOT_FOUND",
                    "message": "Driver not found or not active in this fleet",
                }

            # Validate vehicle exists and is active
            vehicle = (
                db.query(SimpleVehicle)
                .filter(
                    SimpleVehicle.id == vehicle_id,
                    SimpleVehicle.fleet_id == fleet_id,
                )
                .first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found or not active in this fleet",
                }

            # Check if driver is already assigned to another vehicle
            existing_driver_assignment = (
                db.query(VehicleAssignment)
                .filter(
                    VehicleAssignment.driver_id == driver_id,
                    VehicleAssignment.is_active == True,
                )
                .first()
            )

            if existing_driver_assignment:
                return False, {
                    "error_code": "DRIVER_ALREADY_ASSIGNED",
                    "message": f"Driver is already assigned to vehicle {existing_driver_assignment.vehicle_id}",
                }

            # Check if vehicle is already assigned to another driver
            existing_vehicle_assignment = (
                db.query(VehicleAssignment)
                .filter(
                    VehicleAssignment.vehicle_id == vehicle_id,
                    VehicleAssignment.is_active == True,
                )
                .first()
            )

            if existing_vehicle_assignment:
                return False, {
                    "error_code": "VEHICLE_ALREADY_ASSIGNED",
                    "message": f"Vehicle is already assigned to driver {existing_vehicle_assignment.driver_id}",
                }

            # Create new assignment
            assignment = VehicleAssignment(
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                manager_id=manager_id,
                fleet_id=fleet_id,
                assignment_notes=assignment_notes,
                assigned_at=datetime.utcnow(),
                is_active=True,
            )

            db.add(assignment)
            db.commit()
            db.refresh(assignment)

            # Get additional info for response
            driver_name = (
                driver.driver_code
            )  # Use driver code since we don't have first/last name
            vehicle_info = f"{vehicle.fleet_number} ({vehicle.license_plate})"

            logger.info(
                f"Assignment created: Driver {driver_name} assigned to Vehicle {vehicle_info}"
            )

            return True, {
                "message": "Driver assigned to vehicle successfully",
                "assignment": assignment.to_response_dict(driver_name, vehicle_info),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Assignment creation error: {e}")
            return False, {
                "error_code": "ASSIGNMENT_CREATION_FAILED",
                "message": "Failed to create assignment",
            }

    @staticmethod
    def get_fleet_assignments(
        manager_id: str,
        fleet_id: str,
        page: int = 1,
        limit: int = 20,
        active_only: bool = True,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get assignments for a fleet with pagination

        Args:
            manager_id: Manager UUID
            fleet_id: Fleet UUID
            page: Page number
            limit: Items per page
            active_only: Filter for active assignments only
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Build query
            query = db.query(VehicleAssignment).filter(
                VehicleAssignment.fleet_id == fleet_id,
                VehicleAssignment.manager_id == manager_id,
            )

            if active_only:
                query = query.filter(VehicleAssignment.is_active == True)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            assignments = (
                query.order_by(desc(VehicleAssignment.assigned_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Get additional info for each assignment
            assignment_list = []
            for assignment in assignments:
                # Get driver info
                driver = (
                    db.query(SimpleDriver)
                    .filter(SimpleDriver.id == assignment.driver_id)
                    .first()
                )
                driver_name = driver.driver_code if driver else "Unknown Driver"

                # Get vehicle info
                vehicle = (
                    db.query(SimpleVehicle)
                    .filter(SimpleVehicle.id == assignment.vehicle_id)
                    .first()
                )
                vehicle_info = (
                    f"{vehicle.fleet_number} ({vehicle.license_plate})"
                    if vehicle
                    else "Unknown Vehicle"
                )

                assignment_list.append(
                    assignment.to_response_dict(driver_name, vehicle_info)
                )

            total_pages = math.ceil(total_count / limit) if total_count > 0 else 1

            return True, {
                "assignments": assignment_list,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Get fleet assignments error: {e}")
            return False, {
                "error_code": "FETCH_ASSIGNMENTS_FAILED",
                "message": "Failed to fetch assignments",
            }

    @staticmethod
    def unassign_driver(
        assignment_id: str,
        manager_id: str,
        notes: Optional[str],
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Unassign a driver from vehicle

        Args:
            assignment_id: Assignment UUID
            manager_id: Manager UUID
            notes: Optional unassignment notes
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Find assignment
            assignment = (
                db.query(VehicleAssignment)
                .filter(
                    VehicleAssignment.id == assignment_id,
                    VehicleAssignment.manager_id == manager_id,
                    VehicleAssignment.is_active == True,
                )
                .first()
            )

            if not assignment:
                return False, {
                    "error_code": "ASSIGNMENT_NOT_FOUND",
                    "message": "Assignment not found or already inactive",
                }

            # Unassign
            assignment.unassign(notes)
            db.commit()

            logger.info(
                f"Assignment {assignment_id} unassigned by manager {manager_id}"
            )

            return True, {
                "message": "Driver unassigned successfully",
                "assignment_id": assignment_id,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Unassignment error: {e}")
            return False, {
                "error_code": "UNASSIGNMENT_FAILED",
                "message": "Failed to unassign driver",
            }

    @staticmethod
    def get_available_drivers(
        manager_id: str,
        fleet_id: str,
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get drivers available for assignment (not currently assigned)

        Args:
            manager_id: Manager UUID
            fleet_id: Fleet UUID
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get assigned driver IDs
            assigned_driver_ids = (
                db.query(VehicleAssignment.driver_id)
                .filter(VehicleAssignment.is_active == True)
                .subquery()
            )

            # Get available drivers
            available_drivers = (
                db.query(SimpleDriver)
                .filter(
                    SimpleDriver.fleet_id == fleet_id,
                    SimpleDriver.is_active == True,
                    ~SimpleDriver.id.in_(assigned_driver_ids),
                )
                .all()
            )

            driver_list = []
            for driver in available_drivers:
                driver_list.append(
                    {
                        "id": str(driver.id),
                        "driver_id": driver.driver_id,
                        "name": driver.driver_code,
                        "phone": driver.phone,
                        "license_number": driver.license_number,
                    }
                )

            return True, {"available_drivers": driver_list, "count": len(driver_list)}

        except Exception as e:
            logger.error(f"Get available drivers error: {e}")
            return False, {
                "error_code": "FETCH_AVAILABLE_DRIVERS_FAILED",
                "message": "Failed to fetch available drivers",
            }

    @staticmethod
    def get_available_vehicles(
        manager_id: str,
        fleet_id: str,
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get vehicles available for assignment (not currently assigned)

        Args:
            manager_id: Manager UUID
            fleet_id: Fleet UUID
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get assigned vehicle IDs
            assigned_vehicle_ids = (
                db.query(VehicleAssignment.vehicle_id)
                .filter(VehicleAssignment.is_active == True)
                .subquery()
            )

            # Get available vehicles
            available_vehicles = (
                db.query(SimpleVehicle)
                .filter(
                    SimpleVehicle.fleet_id == fleet_id,
                    ~SimpleVehicle.id.in_(assigned_vehicle_ids),
                )
                .all()
            )

            vehicle_list = []
            for vehicle in available_vehicles:
                vehicle_list.append(
                    {
                        "id": str(vehicle.id),
                        "fleet_number": vehicle.fleet_number,
                        "license_plate": vehicle.license_plate,
                        "capacity": vehicle.capacity,
                        "status": vehicle.status,
                    }
                )

            return True, {
                "available_vehicles": vehicle_list,
                "count": len(vehicle_list),
            }

        except Exception as e:
            logger.error(f"Get available vehicles error: {e}")
            return False, {
                "error_code": "FETCH_AVAILABLE_VEHICLES_FAILED",
                "message": "Failed to fetch available vehicles",
            }


# Create service instance
assignment_service = AssignmentService()
