"""
Driver ID Generation Service

Generates unique driver IDs in the format DRV-XXXYYY where:
- XXX: Sequential driver number within fleet (001-999)
- YYY: Fleet identifier code (3 characters)
"""

import logging
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.driver_profile import DriverProfile
from app.models.fleet import Fleet

logger = logging.getLogger(__name__)


class DriverIDService:
    """Service for generating unique driver IDs"""

    @staticmethod
    def generate_driver_id(
        fleet_id: str, db: Session
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate unique driver ID for a fleet

        Args:
            fleet_id: Fleet UUID
            db: Database session

        Returns:
            Tuple of (success, driver_id, error_message)
        """
        try:
            # Get fleet information
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return False, "", "Fleet not found"

            # Generate fleet code from fleet name if not exists
            fleet_code = DriverIDService._generate_fleet_code(
                fleet.fleet_code or fleet.name
            )

            # Update fleet with generated code if it doesn't have one
            if not fleet.fleet_code:
                fleet.fleet_code = fleet_code
                db.commit()
            else:
                fleet_code = fleet.fleet_code

            # Get next sequential number for this fleet
            next_number = DriverIDService._get_next_driver_number(fleet_id, db)

            if next_number > 999:
                return (
                    False,
                    "",
                    "Fleet has reached maximum driver capacity (999 drivers)",
                )

            # Format driver ID
            driver_id = f"DRV-{next_number:03d}{fleet_code}"

            # Verify uniqueness (should be unique by design, but double-check)
            existing = (
                db.query(DriverProfile)
                .filter(DriverProfile.driver_id == driver_id)
                .first()
            )
            if existing:
                logger.error(f"Driver ID collision detected: {driver_id}")
                return False, "", "Driver ID generation failed - please try again"

            logger.info(f"Generated driver ID: {driver_id} for fleet {fleet.name}")
            return True, driver_id, None

        except Exception as e:
            logger.error(f"Driver ID generation error: {e}")
            return False, "", "Driver ID generation failed"

    @staticmethod
    def _generate_fleet_code(fleet_name: str) -> str:
        """
        Generate 3-character fleet code from fleet name

        Args:
            fleet_name: Fleet name

        Returns:
            3-character fleet code
        """
        # Remove common words and get meaningful parts
        words = (
            fleet_name.upper()
            .replace("FLEET", "")
            .replace("SACCO", "")
            .replace("MATATU", "")
            .split()
        )

        if len(words) == 0:
            return "FLT"

        # Try to create meaningful code
        if len(words) == 1:
            word = words[0]
            if len(word) >= 3:
                return word[:3]
            else:
                return word.ljust(3, "X")

        # Multiple words - take first letter of each word
        code = ""
        for word in words[:3]:  # Max 3 words
            if word:
                code += word[0]

        # Pad or truncate to 3 characters
        if len(code) < 3:
            code = code.ljust(3, "X")
        else:
            code = code[:3]

        return code

    @staticmethod
    def _get_next_driver_number(fleet_id: str, db: Session) -> int:
        """
        Get next sequential driver number for a fleet

        Args:
            fleet_id: Fleet UUID
            db: Database session

        Returns:
            Next driver number (1-999)
        """
        try:
            # Get count of existing drivers in this fleet
            # Using raw SQL to ensure atomicity and handle concurrent requests
            result = db.execute(
                text(
                    """
                    SELECT COALESCE(MAX(
                        CAST(
                            SUBSTRING(driver_id FROM 5 FOR 3) AS INTEGER
                        )
                    ), 0) + 1 as next_number
                    FROM drivers
                    WHERE fleet_id = :fleet_id
                    AND driver_id ~ '^DRV-[0-9]{3}.*$'
                """
                ),
                {"fleet_id": fleet_id},
            )

            next_number = result.fetchone()[0]
            return min(next_number, 999)  # Cap at 999

        except Exception as e:
            logger.error(f"Error getting next driver number: {e}")
            # Fallback: count all drivers + 1
            count = (
                db.query(DriverProfile)
                .filter(DriverProfile.fleet_id == fleet_id)
                .count()
            )
            return min(count + 1, 999)

    @staticmethod
    def validate_driver_id_format(driver_id: str) -> bool:
        """
        Validate driver ID format

        Args:
            driver_id: Driver ID to validate

        Returns:
            True if valid format, False otherwise
        """
        import re

        pattern = r"^DRV-[0-9]{3}[A-Z]{3}$"
        return bool(re.match(pattern, driver_id))

    @staticmethod
    def extract_fleet_code(driver_id: str) -> Optional[str]:
        """
        Extract fleet code from driver ID

        Args:
            driver_id: Driver ID in format DRV-XXXYYY

        Returns:
            Fleet code (YYY) or None if invalid format
        """
        if DriverIDService.validate_driver_id_format(driver_id):
            return driver_id[-3:]  # Last 3 characters
        return None

    @staticmethod
    def extract_driver_number(driver_id: str) -> Optional[int]:
        """
        Extract driver number from driver ID

        Args:
            driver_id: Driver ID in format DRV-XXXYYY

        Returns:
            Driver number (XXX) or None if invalid format
        """
        if DriverIDService.validate_driver_id_format(driver_id):
            try:
                return int(driver_id[4:7])  # Characters 4-6 (XXX)
            except ValueError:
                return None
        return None
