"""
Trip Status Service for Real-time Trip Tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from math import ceil
from decimal import Decimal

from app.models.trip import Trip
from app.models.trip_status import (
    TripStatusUpdate,
    GPSLocation,
    NotificationPreference,
    TripStatusEnum,
    UpdateSourceEnum,
)
from app.models.simple_vehicle import SimpleVehicle
from app.models.simple_driver import SimpleDriver
from app.models.user_profile import UserProfile
from app.models.booking import Booking
from app.schemas.trip_status import (
    TripStatusUpdateRequest,
    GPSLocationRequest,
    NotificationPreferenceRequest,
    DelayAlertRequest,
)

logger = logging.getLogger(__name__)


class TripStatusService:
    """Service for managing real-time trip status updates"""

    @staticmethod
    def update_trip_status(
        trip_id: str,
        request: TripStatusUpdateRequest,
        updated_by: Optional[str] = None,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update trip status and create status history record

        Args:
            trip_id: Trip UUID
            request: Status update request
            updated_by: User ID making the update
            db: Database session

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Get trip
            trip = db.query(Trip).filter(Trip.id == trip_id).first()

            if not trip:
                return False, {
                    "error_code": "TRIP_NOT_FOUND",
                    "message": "Trip not found",
                }

            # Create status update record
            status_update = TripStatusUpdate(
                trip_id=trip_id,
                status=request.status,
                location_lat=request.location_lat,
                location_lng=request.location_lng,
                location_name=request.location_name,
                estimated_arrival=request.estimated_arrival,
                delay_minutes=request.delay_minutes or 0,
                update_source=request.update_source,
                notes=request.notes,
                updated_by=updated_by,
            )

            # Update trip status and timing
            previous_status = trip.status
            trip.status = request.status.value

            # Update actual departure/arrival times based on status
            if request.status == TripStatusEnum.DEPARTED and not trip.actual_departure:
                trip.actual_departure = datetime.utcnow()
            elif request.status == TripStatusEnum.COMPLETED and not trip.actual_arrival:
                trip.actual_arrival = datetime.utcnow()

            # Update estimated arrival if provided
            if request.estimated_arrival:
                trip.scheduled_arrival = request.estimated_arrival

            db.add(status_update)
            db.commit()
            db.refresh(status_update)

            logger.info(
                f"Trip status updated: {trip.trip_code} from {previous_status} to {request.status.value}"
            )

            # TODO: Send notifications to passengers
            # self._send_status_notifications(trip, status_update, db)

            return True, {
                "message": "Trip status updated successfully",
                "trip_id": trip_id,
                "previous_status": previous_status,
                "new_status": request.status.value,
                "status_update": status_update.to_dict(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Status update error: {e}")
            return False, {
                "error_code": "UPDATE_FAILED",
                "message": f"Failed to update trip status: {str(e)}",
            }

    @staticmethod
    def get_trip_status_history(
        trip_id: str,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get trip status update history with pagination"""
        try:
            # Check if trip exists
            trip = db.query(Trip).filter(Trip.id == trip_id).first()
            if not trip:
                return False, {
                    "error_code": "TRIP_NOT_FOUND",
                    "message": "Trip not found",
                }

            # Get total count
            total_count = (
                db.query(TripStatusUpdate)
                .filter(TripStatusUpdate.trip_id == trip_id)
                .count()
            )

            # Calculate pagination
            offset = (page - 1) * limit
            total_pages = ceil(total_count / limit) if total_count > 0 else 1

            # Get status updates
            status_updates = (
                db.query(TripStatusUpdate)
                .filter(TripStatusUpdate.trip_id == trip_id)
                .order_by(desc(TripStatusUpdate.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Convert to response format
            status_updates_data = []
            for update in status_updates:
                update_data = update.to_dict()

                # Add updater name if available
                if update.updated_by:
                    updater = (
                        db.query(UserProfile)
                        .filter(UserProfile.id == update.updated_by)
                        .first()
                    )
                    update_data["updated_by_name"] = (
                        updater.full_name if updater else "Unknown User"
                    )

                status_updates_data.append(update_data)

            return True, {
                "status_updates": status_updates_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Get status history error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": f"Failed to fetch status history: {str(e)}",
            }

    @staticmethod
    def record_gps_location(
        request: GPSLocationRequest,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Record GPS location for a vehicle"""
        try:
            # Verify vehicle exists
            vehicle = (
                db.query(SimpleVehicle)
                .filter(SimpleVehicle.id == request.vehicle_id)
                .first()
            )
            if not vehicle:
                return False, {
                    "error_code": "VEHICLE_NOT_FOUND",
                    "message": "Vehicle not found",
                }

            # Verify trip exists if provided
            if request.trip_id:
                trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
                if not trip:
                    return False, {
                        "error_code": "TRIP_NOT_FOUND",
                        "message": "Trip not found",
                    }

            # Create GPS location record
            gps_location = GPSLocation(
                vehicle_id=request.vehicle_id,
                trip_id=request.trip_id,
                latitude=request.latitude,
                longitude=request.longitude,
                altitude=request.altitude,
                speed_kmh=request.speed_kmh,
                heading=request.heading,
                accuracy_meters=request.accuracy_meters,
                recorded_at=request.recorded_at,
            )

            db.add(gps_location)
            db.commit()
            db.refresh(gps_location)

            logger.info(f"GPS location recorded for vehicle {request.vehicle_id}")

            # TODO: Check for geofence alerts and automatic status updates
            # self._check_geofence_alerts(gps_location, db)

            return True, {
                "message": "GPS location recorded successfully",
                "location": gps_location.to_dict(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"GPS location recording error: {e}")
            return False, {
                "error_code": "RECORDING_FAILED",
                "message": f"Failed to record GPS location: {str(e)}",
            }

    @staticmethod
    def get_current_trip_location(
        trip_id: str,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get current GPS location for a trip"""
        try:
            # Get trip and vehicle
            trip = db.query(Trip).filter(Trip.id == trip_id).first()
            if not trip:
                return False, {
                    "error_code": "TRIP_NOT_FOUND",
                    "message": "Trip not found",
                }

            # Get latest GPS location for the trip's vehicle
            latest_location = (
                db.query(GPSLocation)
                .filter(GPSLocation.vehicle_id == trip.vehicle_id)
                .order_by(desc(GPSLocation.recorded_at))
                .first()
            )

            if not latest_location:
                return False, {
                    "error_code": "NO_LOCATION_DATA",
                    "message": "No GPS data available for this trip",
                }

            return True, {
                "trip_id": trip_id,
                "current_location": latest_location.to_dict(),
            }

        except Exception as e:
            logger.error(f"Get current location error: {e}")
            return False, {
                "error_code": "FETCH_FAILED",
                "message": f"Failed to get current location: {str(e)}",
            }

    @staticmethod
    def get_fleet_tracking_dashboard(
        fleet_id: str,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get real-time fleet tracking dashboard data"""
        try:
            # Get active trips for the fleet
            active_trips = (
                db.query(Trip)
                .filter(
                    and_(
                        Trip.fleet_id == fleet_id,
                        Trip.status.in_(["scheduled", "departed", "in_transit"]),
                    )
                )
                .all()
            )

            # Get today's completed and cancelled trips
            today = datetime.utcnow().date()
            completed_today = (
                db.query(Trip)
                .filter(
                    and_(
                        Trip.fleet_id == fleet_id,
                        Trip.status == "completed",
                        func.date(Trip.actual_arrival) == today,
                    )
                )
                .count()
            )

            cancelled_today = (
                db.query(Trip)
                .filter(
                    and_(
                        Trip.fleet_id == fleet_id,
                        Trip.status == "cancelled",
                        func.date(Trip.updated_at) == today,
                    )
                )
                .count()
            )

            # Process active trips data
            active_trips_data = []
            delayed_count = 0
            on_time_count = 0
            total_delay_minutes = 0

            for trip in active_trips:
                # Get latest status update
                latest_update = (
                    db.query(TripStatusUpdate)
                    .filter(TripStatusUpdate.trip_id == trip.id)
                    .order_by(desc(TripStatusUpdate.created_at))
                    .first()
                )

                # Get current location
                current_location = (
                    db.query(GPSLocation)
                    .filter(GPSLocation.vehicle_id == trip.vehicle_id)
                    .order_by(desc(GPSLocation.recorded_at))
                    .first()
                )

                # Calculate delay
                delay_minutes = 0
                if latest_update:
                    delay_minutes = latest_update.delay_minutes

                if delay_minutes > 5:  # Consider 5+ minutes as delayed
                    delayed_count += 1
                    total_delay_minutes += delay_minutes
                else:
                    on_time_count += 1

                # Get vehicle and driver info
                vehicle = (
                    db.query(SimpleVehicle)
                    .filter(SimpleVehicle.id == trip.vehicle_id)
                    .first()
                )
                driver = (
                    db.query(SimpleDriver)
                    .filter(SimpleDriver.id == trip.driver_id)
                    .first()
                )

                trip_data = {
                    "trip_id": str(trip.id),
                    "trip_code": trip.trip_code,
                    "current_status": (
                        latest_update.status.value if latest_update else trip.status
                    ),
                    "scheduled_departure": trip.scheduled_departure.isoformat(),
                    "scheduled_arrival": (
                        trip.scheduled_arrival.isoformat()
                        if trip.scheduled_arrival
                        else None
                    ),
                    "actual_departure": (
                        trip.actual_departure.isoformat()
                        if trip.actual_departure
                        else None
                    ),
                    "estimated_arrival": (
                        latest_update.estimated_arrival.isoformat()
                        if latest_update and latest_update.estimated_arrival
                        else None
                    ),
                    "delay_minutes": delay_minutes,
                    "current_location": (
                        current_location.to_dict() if current_location else None
                    ),
                    "route_name": f"Route {trip.route_id}",  # TODO: Get actual route name
                    "origin_name": "Origin",  # TODO: Get from route
                    "destination_name": "Destination",  # TODO: Get from route
                    "vehicle_info": (
                        f"{vehicle.fleet_number} ({vehicle.license_plate})"
                        if vehicle
                        else "Unknown Vehicle"
                    ),
                    "driver_name": driver.driver_code if driver else "Unknown Driver",
                }

                active_trips_data.append(trip_data)

            # Calculate statistics
            total_active = len(active_trips)
            average_delay = (
                Decimal(total_delay_minutes / delayed_count)
                if delayed_count > 0
                else None
            )
            on_time_percentage = (
                Decimal((on_time_count / total_active) * 100)
                if total_active > 0
                else None
            )

            return True, {
                "active_trips": active_trips_data,
                "total_active_trips": total_active,
                "delayed_trips": delayed_count,
                "on_time_trips": on_time_count,
                "completed_trips_today": completed_today,
                "cancelled_trips_today": cancelled_today,
                "average_delay_minutes": average_delay,
                "on_time_percentage": on_time_percentage,
            }

        except Exception as e:
            logger.error(f"Fleet tracking dashboard error: {e}")
            return False, {
                "error_code": "DASHBOARD_FAILED",
                "message": f"Failed to get fleet tracking data: {str(e)}",
            }

    @staticmethod
    def create_delay_alert(
        request: DelayAlertRequest,
        manager_id: str,
        db: Session = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create delay alert and notify passengers"""
        try:
            # Get trip
            trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
            if not trip:
                return False, {
                    "error_code": "TRIP_NOT_FOUND",
                    "message": "Trip not found",
                }

            # Create status update for delay
            status_update = TripStatusUpdate(
                trip_id=request.trip_id,
                status=TripStatusEnum.DELAYED,
                delay_minutes=request.delay_minutes,
                estimated_arrival=request.estimated_arrival,
                update_source=UpdateSourceEnum.MANUAL,
                notes=request.reason,
                updated_by=manager_id,
            )

            # Update trip status
            trip.status = TripStatusEnum.DELAYED.value
            if request.estimated_arrival:
                trip.scheduled_arrival = request.estimated_arrival

            db.add(status_update)
            db.commit()

            # Get affected passengers
            bookings = (
                db.query(Booking).filter(Booking.trip_id == request.trip_id).all()
            )
            affected_passengers = len(bookings)

            logger.info(
                f"Delay alert created for trip {trip.trip_code}: {request.delay_minutes} minutes"
            )

            # TODO: Send notifications to passengers
            notifications_sent = 0  # Placeholder

            return True, {
                "success": True,
                "message": f"Delay alert created for {request.delay_minutes} minutes",
                "trip_id": request.trip_id,
                "delay_minutes": request.delay_minutes,
                "notifications_sent": notifications_sent,
                "affected_passengers": affected_passengers,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Delay alert error: {e}")
            return False, {
                "error_code": "ALERT_FAILED",
                "message": f"Failed to create delay alert: {str(e)}",
            }
