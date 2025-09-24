"""
Admin service for manager account management
"""

import logging
import secrets
import string
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user_profile import UserProfile, UserRole
from app.models.fleet import Fleet
from app.models.audit_log import AuditLog
from app.core.supabase_client import supabase_client
from app.services.sms_service import SMSService
from app.utils.phone_validator import PhoneValidator

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations on manager accounts"""

    def __init__(self):
        self.sms_service = SMSService()

    def create_manager(
        self,
        phone: str,
        first_name: str,
        last_name: str,
        fleet_name: Optional[str],
        created_by_admin_id: str,
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new manager account

        Args:
            phone: Manager's phone number
            first_name: Manager's first name
            last_name: Manager's last name
            fleet_name: Optional fleet to assign manager to
            created_by_admin_id: ID of admin creating the manager
            db: Database session

        Returns:
            Tuple[bool, Dict]: Success status and response data
        """
        try:
            # Check if phone already exists
            existing_user = (
                db.query(UserProfile).filter(UserProfile.phone == phone).first()
            )
            if existing_user:
                return False, {
                    "error_code": "PHONE_EXISTS",
                    "message": f"User with phone {phone} already exists",
                }

            # Check if fleet exists (if provided)
            fleet = None
            if fleet_name:
                fleet = db.query(Fleet).filter(Fleet.name == fleet_name).first()
                if not fleet:
                    return False, {
                        "error_code": "FLEET_NOT_FOUND",
                        "message": f"Fleet '{fleet_name}' not found",
                    }

            # Generate temporary access code
            temp_access_code = self._generate_temporary_access_code()

            # Create manager in local database
            manager_user_id = uuid.uuid4()
            manager = UserProfile(
                user_id=manager_user_id,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.MANAGER,
                is_active=True,
                fleet_id=fleet.id if fleet else None,
                temporary_access_code=temp_access_code,
                created_by_admin_id=created_by_admin_id,
            )

            db.add(manager)
            db.flush()  # Get the ID without committing

            # Create manager in Supabase (temporarily disabled for testing)
            # try:
            #     supabase_response = supabase_client.table("user_profiles").insert({
            #         "user_id": str(manager.user_id),
            #         "phone": phone,
            #         "first_name": first_name,
            #         "last_name": last_name,
            #         "role": "manager",
            #         "is_active": True,
            #         "fleet_id": str(fleet.id) if fleet else None,
            #         "created_by_admin_id": created_by_admin_id,
            #     }).execute()

            #     if not supabase_response.data:
            #         logger.error("Failed to create manager in Supabase")
            #         db.rollback()
            #         return False, {
            #             "error_code": "SUPABASE_ERROR",
            #             "message": "Failed to create manager in cloud database",
            #         }

            # except Exception as e:
            #     logger.error(f"Supabase manager creation error: {e}")
            #     db.rollback()
            #     return False, {
            #         "error_code": "SUPABASE_ERROR",
            #         "message": "Failed to create manager in cloud database",
            #     }

            # Log admin action
            audit_log = AuditLog(
                admin_id=created_by_admin_id,
                action="CREATE_MANAGER",
                target_user_id=str(manager.user_id),
                details={
                    "manager_phone": phone,
                    "manager_name": f"{first_name} {last_name}",
                    "fleet_name": fleet_name,
                },
            )
            db.add(audit_log)

            # Send welcome SMS with temporary access code
            welcome_message = (
                f"Welcome to Rembo Matatu Fleet Management! "
                f"You've been added as a manager. "
                f"Your temporary access code is: {temp_access_code}. "
                f"Please login and change your credentials."
            )

            sms_sent = self.sms_service.send_sms(phone, welcome_message)
            if not sms_sent:
                logger.warning(f"Failed to send welcome SMS to manager {phone}")

            db.commit()

            # Prepare response
            manager_response = {
                "user_id": manager.user_id,
                "phone": manager.phone,
                "first_name": manager.first_name,
                "last_name": manager.last_name,
                "role": manager.role.value,
                "is_active": manager.is_active,
                "fleet_name": fleet.name if fleet else None,
                "created_at": manager.created_at.isoformat(),
                "last_login": None,
            }

            return True, {
                "success": True,
                "message": "Manager account created successfully",
                "manager": manager_response,
                "temporary_access_code": temp_access_code,
            }

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating manager: {e}")
            return False, {
                "error_code": "INTEGRITY_ERROR",
                "message": "Manager creation failed due to data conflict",
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Manager creation error: {e}")
            return False, {
                "error_code": "UNKNOWN_ERROR",
                "message": "Manager creation failed",
            }

    def list_managers(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        List all manager accounts

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Filter for active managers only
            db: Database session

        Returns:
            Tuple[bool, Dict]: Success status and response data
        """
        try:
            # Build query
            query = db.query(UserProfile).filter(UserProfile.role == UserRole.MANAGER)

            if active_only:
                query = query.filter(UserProfile.is_active == True)

            # Get total count
            total_count = query.count()

            # Get managers with pagination
            managers = query.offset(skip).limit(limit).all()

            # Format response
            manager_list = []
            for manager in managers:
                fleet_name = None
                if manager.fleet_id:
                    fleet = db.query(Fleet).filter(Fleet.id == manager.fleet_id).first()
                    fleet_name = fleet.name if fleet else None

                manager_data = {
                    "user_id": manager.user_id,
                    "phone": manager.phone,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "role": manager.role.value,
                    "is_active": manager.is_active,
                    "fleet_name": fleet_name,
                    "created_at": manager.created_at.isoformat(),
                    "last_login": (
                        manager.last_login.isoformat() if manager.last_login else None
                    ),
                }
                manager_list.append(manager_data)

            return True, {
                "managers": manager_list,
                "total_count": total_count,
            }

        except Exception as e:
            logger.error(f"Manager list error: {e}")
            return False, {
                "error_code": "UNKNOWN_ERROR",
                "message": "Failed to retrieve managers",
            }

    def get_manager(self, manager_id: str, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """
        Get manager details by ID

        Args:
            manager_id: Manager's user ID
            db: Database session

        Returns:
            Tuple[bool, Dict]: Success status and response data
        """
        try:
            manager = (
                db.query(UserProfile)
                .filter(
                    UserProfile.user_id == manager_id,
                    UserProfile.role == UserRole.MANAGER,
                )
                .first()
            )

            if not manager:
                return False, {
                    "error_code": "MANAGER_NOT_FOUND",
                    "message": "Manager not found",
                }

            # Get fleet information
            fleet_name = None
            if manager.fleet_id:
                fleet = db.query(Fleet).filter(Fleet.id == manager.fleet_id).first()
                fleet_name = fleet.name if fleet else None

            manager_data = {
                "user_id": manager.user_id,
                "phone": manager.phone,
                "first_name": manager.first_name,
                "last_name": manager.last_name,
                "role": manager.role.value,
                "is_active": manager.is_active,
                "fleet_name": fleet_name,
                "created_at": manager.created_at.isoformat(),
                "last_login": (
                    manager.last_login.isoformat() if manager.last_login else None
                ),
            }

            return True, {"manager": manager_data}

        except Exception as e:
            logger.error(f"Get manager error: {e}")
            return False, {
                "error_code": "UNKNOWN_ERROR",
                "message": "Failed to retrieve manager",
            }

    def activate_manager(
        self, manager_id: str, admin_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Activate a manager account

        Args:
            manager_id: Manager's user ID
            admin_id: Admin performing the action
            db: Database session

        Returns:
            Tuple[bool, Dict]: Success status and response data
        """
        try:
            manager = (
                db.query(UserProfile)
                .filter(
                    UserProfile.user_id == manager_id,
                    UserProfile.role == UserRole.MANAGER,
                )
                .first()
            )

            if not manager:
                return False, {
                    "error_code": "MANAGER_NOT_FOUND",
                    "message": "Manager not found",
                }

            # Update manager status
            manager.is_active = True

            # Update in Supabase
            try:
                supabase_client.table("user_profiles").update({"is_active": True}).eq(
                    "user_id", manager_id
                ).execute()
            except Exception as e:
                logger.error(f"Supabase manager activation error: {e}")

            # Log admin action
            audit_log = AuditLog(
                admin_id=admin_id,
                action="ACTIVATE_MANAGER",
                target_user_id=manager_id,
                details={"manager_phone": manager.phone},
            )
            db.add(audit_log)

            db.commit()

            return True, {
                "success": True,
                "message": "Manager account activated successfully",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Manager activation error: {e}")
            return False, {
                "error_code": "UNKNOWN_ERROR",
                "message": "Manager activation failed",
            }

    def deactivate_manager(
        self, manager_id: str, admin_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Deactivate a manager account

        Args:
            manager_id: Manager's user ID
            admin_id: Admin performing the action
            db: Database session

        Returns:
            Tuple[bool, Dict]: Success status and response data
        """
        try:
            manager = (
                db.query(UserProfile)
                .filter(
                    UserProfile.user_id == manager_id,
                    UserProfile.role == UserRole.MANAGER,
                )
                .first()
            )

            if not manager:
                return False, {
                    "error_code": "MANAGER_NOT_FOUND",
                    "message": "Manager not found",
                }

            # Update manager status
            manager.is_active = False

            # Update in Supabase
            try:
                supabase_client.table("user_profiles").update({"is_active": False}).eq(
                    "user_id", manager_id
                ).execute()
            except Exception as e:
                logger.error(f"Supabase manager deactivation error: {e}")

            # Log admin action
            audit_log = AuditLog(
                admin_id=admin_id,
                action="DEACTIVATE_MANAGER",
                target_user_id=manager_id,
                details={"manager_phone": manager.phone},
            )
            db.add(audit_log)

            db.commit()

            return True, {
                "success": True,
                "message": "Manager account deactivated successfully",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Manager deactivation error: {e}")
            return False, {
                "error_code": "UNKNOWN_ERROR",
                "message": "Manager deactivation failed",
            }

    def _generate_temporary_access_code(self) -> str:
        """
        Generate a secure temporary access code for new managers

        Returns:
            str: Temporary access code
        """
        # Generate 8-character alphanumeric code
        characters = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(characters) for _ in range(8))

    @staticmethod
    def create_default_fleets(db: Session) -> None:
        """
        Create default fleets for testing and initial setup

        Args:
            db: Database session
        """
        try:
            # Check if fleets already exist
            existing_fleets = db.query(Fleet).count()
            if existing_fleets > 0:
                logger.info("Fleets already exist, skipping default fleet creation")
                return

            # Create default fleets
            default_fleets = [
                {
                    "name": "Nairobi City Shuttles",
                    "fleet_code": "NCS001",
                    "description": "Main city routes covering CBD and residential areas",
                },
                {
                    "name": "Eastlands Express",
                    "fleet_code": "EE002",
                    "description": "Routes covering Eastlands area including Kayole, Umoja, Donholm",
                },
                {
                    "name": "Westlands Commuter",
                    "fleet_code": "WC003",
                    "description": "Premium routes for Westlands, Parklands, and Highridge",
                },
            ]

            for fleet_data in default_fleets:
                fleet = Fleet(**fleet_data)
                db.add(fleet)

            db.commit()
            logger.info(f"Created {len(default_fleets)} default fleets")

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default fleets: {e}")
