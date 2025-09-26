"""
Vehicle status and maintenance tracking service
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from math import ceil

from app.models.simple_vehicle import SimpleVehicle
from app.models.vehicle_status import (
    VehicleStatusHistory,
    MaintenanceRecord,
    VehicleDocument,
    VehicleInspection,
    VehicleStatusEnum,
    MaintenanceTypeEnum,
    MaintenancePriorityEnum,
)
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)


class VehicleStatusService:
    """Service for managing vehicle status and maintenance"""

    @staticmethod
    def change_vehicle_status(
        vehicle_id: str,
        new_status: VehicleStatusEnum,
        manager_id: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Change vehicle status and record history

        Args:
            vehicle_id: Vehicle UUID
            new_status: New status to set
            manager_id: Manager making the change
            reason: Reason for status change
            notes: Additional notes
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get vehicle
            vehicle = (
                db.query(SimpleVehicle).filter(SimpleVehicle.id == vehicle_id).first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            # Get manager profile
            manager = db.query(UserProfile).filter(UserProfile.id == manager_id).first()
            if not manager:
                return False, {
                    "error_code": "MANAGER_NOT_FOUND",
                    "message": "Manager not found",
                }

            # Check if manager has access to this vehicle's fleet
            if str(vehicle.fleet_id) != str(manager.fleet_id):
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this vehicle",
                }

            # Record status change
            previous_status = vehicle.status

            # Create status history record
            status_history = VehicleStatusHistory(
                vehicle_id=vehicle_id,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=manager_id,
                reason=reason,
                notes=notes,
            )

            # Update vehicle status
            vehicle.status = new_status.value
            vehicle.updated_at = datetime.utcnow()

            db.add(status_history)
            db.commit()

            return True, {
                "message": "Vehicle status updated successfully",
                "vehicle_id": vehicle_id,
                "previous_status": previous_status,
                "new_status": new_status.value,
                "changed_at": status_history.changed_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Status change error: {e}")
            db.rollback()
            return False, {
                "error_code": "STATUS_CHANGE_FAILED",
                "message": "Failed to change vehicle status",
            }

    @staticmethod
    def get_vehicle_status_history(
        vehicle_id: str,
        manager_id: str,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get vehicle status history with pagination"""
        try:
            # Verify access
            vehicle = (
                db.query(SimpleVehicle).filter(SimpleVehicle.id == vehicle_id).first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            manager = db.query(UserProfile).filter(UserProfile.id == manager_id).first()
            if not manager or str(vehicle.fleet_id) != str(manager.fleet_id):
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this vehicle",
                }

            # Get status history with pagination
            offset = (page - 1) * limit

            query = (
                db.query(VehicleStatusHistory)
                .filter(VehicleStatusHistory.vehicle_id == vehicle_id)
                .order_by(desc(VehicleStatusHistory.changed_at))
            )

            total_count = query.count()
            history_records = query.offset(offset).limit(limit).all()

            # Format response
            history_list = []
            for record in history_records:
                # Get user name
                user = (
                    db.query(UserProfile)
                    .filter(UserProfile.id == record.changed_by)
                    .first()
                )
                user_name = (
                    f"{user.first_name} {user.last_name}"
                    if user and user.first_name
                    else None
                )

                history_list.append(
                    {
                        "id": str(record.id),
                        "vehicle_id": str(record.vehicle_id),
                        "previous_status": record.previous_status,
                        "new_status": record.new_status,
                        "changed_by": str(record.changed_by),
                        "changed_by_name": user_name,
                        "reason": record.reason,
                        "notes": record.notes,
                        "changed_at": record.changed_at.isoformat(),
                        "created_at": record.created_at.isoformat(),
                    }
                )

            total_pages = ceil(total_count / limit)

            return True, {
                "status_history": history_list,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Get status history error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": "Failed to retrieve status history",
            }

    @staticmethod
    def create_maintenance_record(
        vehicle_id: str,
        manager_id: str,
        maintenance_data: Dict[str, Any],
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new maintenance record"""
        try:
            # Verify access
            vehicle = (
                db.query(SimpleVehicle).filter(SimpleVehicle.id == vehicle_id).first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            manager = db.query(UserProfile).filter(UserProfile.id == manager_id).first()
            if not manager or str(vehicle.fleet_id) != str(manager.fleet_id):
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this vehicle",
                }

            # Create maintenance record
            maintenance_record = MaintenanceRecord(
                vehicle_id=vehicle_id, created_by=manager_id, **maintenance_data
            )

            db.add(maintenance_record)
            db.commit()

            # Format response
            vehicle_info = f"{vehicle.fleet_number} ({vehicle.license_plate})"

            return True, {
                "message": "Maintenance record created successfully",
                "maintenance_record": {
                    "id": str(maintenance_record.id),
                    "vehicle_id": str(maintenance_record.vehicle_id),
                    "vehicle_info": vehicle_info,
                    "maintenance_type": maintenance_record.maintenance_type,
                    "priority": maintenance_record.priority,
                    "title": maintenance_record.title,
                    "description": maintenance_record.description,
                    "scheduled_date": (
                        maintenance_record.scheduled_date.isoformat()
                        if maintenance_record.scheduled_date
                        else None
                    ),
                    "started_at": (
                        maintenance_record.started_at.isoformat()
                        if maintenance_record.started_at
                        else None
                    ),
                    "completed_at": (
                        maintenance_record.completed_at.isoformat()
                        if maintenance_record.completed_at
                        else None
                    ),
                    "assigned_to": maintenance_record.assigned_to,
                    "performed_by": maintenance_record.performed_by,
                    "created_by": str(maintenance_record.created_by),
                    "estimated_cost": maintenance_record.estimated_cost,
                    "actual_cost": maintenance_record.actual_cost,
                    "is_completed": maintenance_record.is_completed,
                    "is_approved": maintenance_record.is_approved,
                    "odometer_reading": maintenance_record.odometer_reading,
                    "next_service_km": maintenance_record.next_service_km,
                    "next_service_date": (
                        maintenance_record.next_service_date.isoformat()
                        if maintenance_record.next_service_date
                        else None
                    ),
                    "created_at": maintenance_record.created_at.isoformat(),
                    "updated_at": maintenance_record.updated_at.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Create maintenance record error: {e}")
            db.rollback()
            return False, {
                "error_code": "CREATE_FAILED",
                "message": "Failed to create maintenance record",
            }

    @staticmethod
    def get_fleet_maintenance_records(
        manager_id: str,
        fleet_id: str,
        page: int = 1,
        limit: int = 20,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get maintenance records for fleet with filtering"""
        try:
            # Verify manager access
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(UserProfile.id == manager_id, UserProfile.fleet_id == fleet_id)
                )
                .first()
            )

            if not manager:
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this fleet",
                }

            # Build query
            query = (
                db.query(MaintenanceRecord)
                .join(SimpleVehicle)
                .filter(SimpleVehicle.fleet_id == fleet_id)
            )

            # Apply filters
            if status_filter == "pending":
                query = query.filter(MaintenanceRecord.is_completed == False)
            elif status_filter == "completed":
                query = query.filter(MaintenanceRecord.is_completed == True)

            if priority_filter:
                query = query.filter(MaintenanceRecord.priority == priority_filter)

            # Order by priority and date
            query = query.order_by(
                MaintenanceRecord.priority.desc(),
                MaintenanceRecord.scheduled_date.asc().nullslast(),
                MaintenanceRecord.created_at.desc(),
            )

            # Pagination
            offset = (page - 1) * limit
            total_count = query.count()
            records = query.offset(offset).limit(limit).all()

            # Format response
            maintenance_list = []
            for record in records:
                vehicle = (
                    db.query(SimpleVehicle)
                    .filter(SimpleVehicle.id == record.vehicle_id)
                    .first()
                )
                vehicle_info = (
                    f"{vehicle.fleet_number} ({vehicle.license_plate})"
                    if vehicle
                    else "Unknown Vehicle"
                )

                maintenance_list.append(
                    {
                        "id": str(record.id),
                        "vehicle_id": str(record.vehicle_id),
                        "vehicle_info": vehicle_info,
                        "maintenance_type": record.maintenance_type,
                        "priority": record.priority,
                        "title": record.title,
                        "description": record.description,
                        "scheduled_date": (
                            record.scheduled_date.isoformat()
                            if record.scheduled_date
                            else None
                        ),
                        "started_at": (
                            record.started_at.isoformat() if record.started_at else None
                        ),
                        "completed_at": (
                            record.completed_at.isoformat()
                            if record.completed_at
                            else None
                        ),
                        "assigned_to": record.assigned_to,
                        "performed_by": record.performed_by,
                        "created_by": str(record.created_by),
                        "estimated_cost": record.estimated_cost,
                        "actual_cost": record.actual_cost,
                        "is_completed": record.is_completed,
                        "is_approved": record.is_approved,
                        "odometer_reading": record.odometer_reading,
                        "next_service_km": record.next_service_km,
                        "next_service_date": (
                            record.next_service_date.isoformat()
                            if record.next_service_date
                            else None
                        ),
                        "created_at": record.created_at.isoformat(),
                        "updated_at": record.updated_at.isoformat(),
                    }
                )

            total_pages = ceil(total_count / limit)

            return True, {
                "maintenance_records": maintenance_list,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Get maintenance records error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": "Failed to retrieve maintenance records",
            }

    @staticmethod
    def create_vehicle_document(
        vehicle_id: str,
        manager_id: str,
        document_data: Dict[str, Any],
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new vehicle document"""
        try:
            # Verify access
            vehicle = (
                db.query(SimpleVehicle).filter(SimpleVehicle.id == vehicle_id).first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            manager = db.query(UserProfile).filter(UserProfile.id == manager_id).first()
            if not manager or str(vehicle.fleet_id) != str(manager.fleet_id):
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this vehicle",
                }

            # Create document record
            document = VehicleDocument(
                vehicle_id=vehicle_id, uploaded_by=manager_id, **document_data
            )

            db.add(document)
            db.commit()

            return True, {
                "message": "Vehicle document created successfully",
                "document": {
                    "id": str(document.id),
                    "vehicle_id": str(document.vehicle_id),
                    "document_type": document.document_type,
                    "document_number": document.document_number,
                    "issuer": document.issuer,
                    "issued_date": (
                        document.issued_date.isoformat()
                        if document.issued_date
                        else None
                    ),
                    "expiry_date": (
                        document.expiry_date.isoformat()
                        if document.expiry_date
                        else None
                    ),
                    "is_active": document.is_active,
                    "is_expired": document.is_expired,
                    "notes": document.notes,
                    "uploaded_by": str(document.uploaded_by),
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Create document error: {e}")
            db.rollback()
            return False, {
                "error_code": "CREATE_FAILED",
                "message": "Failed to create vehicle document",
            }

    @staticmethod
    def get_vehicle_documents(
        vehicle_id: str,
        manager_id: str,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get vehicle documents with pagination"""
        try:
            # Verify access
            vehicle = (
                db.query(SimpleVehicle).filter(SimpleVehicle.id == vehicle_id).first()
            )

            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            manager = db.query(UserProfile).filter(UserProfile.id == manager_id).first()
            if not manager or str(vehicle.fleet_id) != str(manager.fleet_id):
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this vehicle",
                }

            # Get documents with pagination
            offset = (page - 1) * limit

            query = (
                db.query(VehicleDocument)
                .filter(VehicleDocument.vehicle_id == vehicle_id)
                .order_by(desc(VehicleDocument.created_at))
            )

            total_count = query.count()
            documents = query.offset(offset).limit(limit).all()

            # Format response
            document_list = []
            for doc in documents:
                document_list.append(
                    {
                        "id": str(doc.id),
                        "vehicle_id": str(doc.vehicle_id),
                        "document_type": doc.document_type,
                        "document_number": doc.document_number,
                        "issuer": doc.issuer,
                        "issued_date": (
                            doc.issued_date.isoformat() if doc.issued_date else None
                        ),
                        "expiry_date": (
                            doc.expiry_date.isoformat() if doc.expiry_date else None
                        ),
                        "is_active": doc.is_active,
                        "is_expired": doc.is_expired,
                        "file_path": doc.file_path,
                        "file_name": doc.file_name,
                        "notes": doc.notes,
                        "uploaded_by": str(doc.uploaded_by),
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                    }
                )

            total_pages = ceil(total_count / limit)

            return True, {
                "documents": document_list,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Get documents error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": "Failed to retrieve vehicle documents",
            }

    @staticmethod
    def get_fleet_status_dashboard(
        manager_id: str,
        fleet_id: str,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get fleet status dashboard summary"""
        try:
            # Verify manager access
            manager = (
                db.query(UserProfile)
                .filter(
                    and_(UserProfile.id == manager_id, UserProfile.fleet_id == fleet_id)
                )
                .first()
            )

            if not manager:
                return False, {
                    "error_code": "ACCESS_DENIED",
                    "message": "Access denied to this fleet",
                }

            # Get fleet vehicles
            vehicles = (
                db.query(SimpleVehicle).filter(SimpleVehicle.fleet_id == fleet_id).all()
            )

            # Count vehicles by status
            total_vehicles = len(vehicles)
            active_vehicles = sum(1 for v in vehicles if v.status == "active")
            maintenance_vehicles = sum(1 for v in vehicles if v.status == "maintenance")
            out_of_service_vehicles = sum(
                1 for v in vehicles if v.status == "out_of_service"
            )

            # Count pending maintenance
            pending_maintenance = (
                db.query(MaintenanceRecord)
                .join(SimpleVehicle)
                .filter(
                    and_(
                        SimpleVehicle.fleet_id == fleet_id,
                        MaintenanceRecord.is_completed == False,
                    )
                )
                .count()
            )

            # Count overdue maintenance (scheduled date passed)
            from datetime import datetime

            overdue_maintenance = (
                db.query(MaintenanceRecord)
                .join(SimpleVehicle)
                .filter(
                    and_(
                        SimpleVehicle.fleet_id == fleet_id,
                        MaintenanceRecord.is_completed == False,
                        MaintenanceRecord.scheduled_date < datetime.utcnow(),
                    )
                )
                .count()
            )

            return True, {
                "total_vehicles": total_vehicles,
                "active_vehicles": active_vehicles,
                "maintenance_vehicles": maintenance_vehicles,
                "out_of_service_vehicles": out_of_service_vehicles,
                "pending_maintenance": pending_maintenance,
                "overdue_maintenance": overdue_maintenance,
                "upcoming_inspections": 0,  # TODO: Implement when inspection system is ready
                "overdue_inspections": 0,  # TODO: Implement when inspection system is ready
                "compliance_issues": 0,  # TODO: Implement compliance checking
            }

        except Exception as e:
            logger.error(f"Get dashboard error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": "Failed to retrieve fleet dashboard",
            }


# Create service instance
vehicle_status_service = VehicleStatusService()
