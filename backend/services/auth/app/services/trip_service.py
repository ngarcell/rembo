"""
Trip Service for Trip Creation & Scheduling
"""

import logging
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from decimal import Decimal

from app.models.trip import Route, Trip, TripTemplate, TripStatus
from app.models.simple_vehicle import SimpleVehicle
from app.models.simple_driver import SimpleDriver
from app.models.vehicle_assignment import VehicleAssignment
from app.schemas.trip import (
    RouteCreateRequest,
    RouteUpdateRequest,
    TripCreateRequest,
    TripUpdateRequest,
    TripTemplateCreateRequest,
    BulkTripCreateRequest,
    AvailabilityCheckRequest,
)

logger = logging.getLogger(__name__)


class TripService:
    """Service class for trip and route management"""

    @staticmethod
    def create_route(
        fleet_id: str, request: RouteCreateRequest, manager_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new route"""
        try:
            # Check if route code already exists in this fleet
            existing_route = (
                db.query(Route)
                .filter(
                    and_(
                        Route.fleet_id == fleet_id,
                        Route.route_code == request.route_code,
                    )
                )
                .first()
            )

            if existing_route:
                return False, {"error": "Route code already exists in this fleet"}

            # Create new route
            route = Route(
                fleet_id=fleet_id,
                route_code=request.route_code,
                route_name=request.route_name,
                origin_name=request.origin_name,
                destination_name=request.destination_name,
                distance_km=request.distance_km,
                estimated_duration_minutes=request.estimated_duration_minutes,
                base_fare=request.base_fare,
                waypoints=request.waypoints,
                description=request.description,
            )

            db.add(route)
            db.commit()
            db.refresh(route)

            logger.info(f"Route created: {route.route_code} by manager {manager_id}")

            return True, {
                "success": True,
                "message": "Route created successfully",
                "route_id": str(route.id),
                "route": route.to_dict(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating route: {str(e)}")
            return False, {"error": f"Failed to create route: {str(e)}"}

    @staticmethod
    def get_routes(
        fleet_id: str, db: Session, active_only: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get all routes for a fleet"""
        try:
            query = db.query(Route).filter(Route.fleet_id == fleet_id)

            if active_only:
                query = query.filter(Route.is_active == True)

            routes = query.order_by(Route.route_code).all()

            return True, {
                "routes": [route.to_dict() for route in routes],
                "total_count": len(routes),
            }

        except Exception as e:
            logger.error(f"Error retrieving routes: {str(e)}")
            return False, {"error": f"Failed to retrieve routes: {str(e)}"}

    @staticmethod
    def update_route(
        route_id: str, fleet_id: str, request: RouteUpdateRequest, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Update an existing route"""
        try:
            route = (
                db.query(Route)
                .filter(and_(Route.id == route_id, Route.fleet_id == fleet_id))
                .first()
            )

            if not route:
                return False, {"error": "Route not found"}

            # Update fields if provided
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(route, field, value)

            db.commit()
            db.refresh(route)

            logger.info(f"Route updated: {route.route_code}")

            return True, {
                "success": True,
                "message": "Route updated successfully",
                "route": route.to_dict(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating route: {str(e)}")
            return False, {"error": f"Failed to update route: {str(e)}"}

    @staticmethod
    def check_availability(
        fleet_id: str, request: AvailabilityCheckRequest, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check vehicle and driver availability for a time period"""
        try:
            conflicts = []

            # Check vehicle availability
            if request.vehicle_id:
                vehicle_conflicts = (
                    db.query(Trip)
                    .filter(
                        and_(
                            Trip.vehicle_id == request.vehicle_id,
                            Trip.fleet_id == fleet_id,
                            Trip.status.in_(
                                [
                                    TripStatus.SCHEDULED.value,
                                    TripStatus.IN_PROGRESS.value,
                                ]
                            ),
                            or_(
                                and_(
                                    Trip.scheduled_departure <= request.start_datetime,
                                    Trip.scheduled_arrival >= request.start_datetime,
                                ),
                                and_(
                                    Trip.scheduled_departure <= request.end_datetime,
                                    Trip.scheduled_arrival >= request.end_datetime,
                                ),
                                and_(
                                    Trip.scheduled_departure >= request.start_datetime,
                                    Trip.scheduled_departure <= request.end_datetime,
                                ),
                            ),
                        )
                    )
                    .all()
                )

                for conflict in vehicle_conflicts:
                    conflicts.append(
                        {
                            "type": "vehicle",
                            "trip_id": str(conflict.id),
                            "trip_code": conflict.trip_code,
                            "scheduled_departure": conflict.scheduled_departure.isoformat(),
                            "scheduled_arrival": (
                                conflict.scheduled_arrival.isoformat()
                                if conflict.scheduled_arrival
                                else None
                            ),
                        }
                    )

            # Check driver availability
            if request.driver_id:
                driver_conflicts = (
                    db.query(Trip)
                    .filter(
                        and_(
                            Trip.driver_id == request.driver_id,
                            Trip.fleet_id == fleet_id,
                            Trip.status.in_(
                                [
                                    TripStatus.SCHEDULED.value,
                                    TripStatus.IN_PROGRESS.value,
                                ]
                            ),
                            or_(
                                and_(
                                    Trip.scheduled_departure <= request.start_datetime,
                                    Trip.scheduled_arrival >= request.start_datetime,
                                ),
                                and_(
                                    Trip.scheduled_departure <= request.end_datetime,
                                    Trip.scheduled_arrival >= request.end_datetime,
                                ),
                                and_(
                                    Trip.scheduled_departure >= request.start_datetime,
                                    Trip.scheduled_departure <= request.end_datetime,
                                ),
                            ),
                        )
                    )
                    .all()
                )

                for conflict in driver_conflicts:
                    conflicts.append(
                        {
                            "type": "driver",
                            "trip_id": str(conflict.id),
                            "trip_code": conflict.trip_code,
                            "scheduled_departure": conflict.scheduled_departure.isoformat(),
                            "scheduled_arrival": (
                                conflict.scheduled_arrival.isoformat()
                                if conflict.scheduled_arrival
                                else None
                            ),
                        }
                    )

            is_available = len(conflicts) == 0
            message = (
                "Available"
                if is_available
                else f"Conflicts found: {len(conflicts)} overlapping trips"
            )

            return True, {
                "vehicle_id": request.vehicle_id,
                "driver_id": request.driver_id,
                "is_available": is_available,
                "conflicting_trips": conflicts,
                "message": message,
            }

        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return False, {"error": f"Failed to check availability: {str(e)}"}

    @staticmethod
    def generate_trip_code(route_code: str, departure_datetime: datetime) -> str:
        """Generate a unique trip code"""
        date_str = departure_datetime.strftime("%Y%m%d")
        time_str = departure_datetime.strftime("%H%M")
        return f"{route_code}-{date_str}-{time_str}"

    @staticmethod
    def create_trip(
        fleet_id: str, request: TripCreateRequest, manager_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new trip"""
        try:
            # Validate route exists and belongs to fleet
            route = (
                db.query(Route)
                .filter(
                    and_(
                        Route.id == request.route_id,
                        Route.fleet_id == fleet_id,
                        Route.is_active == True,
                    )
                )
                .first()
            )

            if not route:
                return False, {"error": "Route not found or inactive"}

            # Validate vehicle exists and belongs to fleet
            vehicle = (
                db.query(SimpleVehicle)
                .filter(
                    and_(
                        SimpleVehicle.id == request.vehicle_id,
                        SimpleVehicle.fleet_id == fleet_id,
                    )
                )
                .first()
            )

            if not vehicle:
                return False, {"error": "Vehicle not found or not in fleet"}

            # Validate driver exists and belongs to fleet
            driver = (
                db.query(SimpleDriver)
                .filter(
                    and_(
                        SimpleDriver.id == request.driver_id,
                        SimpleDriver.fleet_id == fleet_id,
                    )
                )
                .first()
            )

            if not driver:
                return False, {"error": "Driver not found or not in fleet"}

            # Check availability
            availability_request = AvailabilityCheckRequest(
                vehicle_id=request.vehicle_id,
                driver_id=request.driver_id,
                start_datetime=request.scheduled_departure,
                end_datetime=request.scheduled_arrival
                or (request.scheduled_departure + timedelta(hours=2)),
            )

            available, availability_result = TripService.check_availability(
                fleet_id, availability_request, db
            )
            if not available:
                return False, {"error": "Failed to check availability"}

            if not availability_result["is_available"]:
                return False, {
                    "error": "Vehicle or driver not available for the scheduled time",
                    "conflicts": availability_result["conflicting_trips"],
                }

            # Generate trip code
            trip_code = TripService.generate_trip_code(
                route.route_code, request.scheduled_departure
            )

            # Check if trip code already exists
            existing_trip = db.query(Trip).filter(Trip.trip_code == trip_code).first()
            if existing_trip:
                # Add a suffix to make it unique
                counter = 1
                while existing_trip:
                    new_trip_code = f"{trip_code}-{counter}"
                    existing_trip = (
                        db.query(Trip).filter(Trip.trip_code == new_trip_code).first()
                    )
                    counter += 1
                trip_code = new_trip_code

            # Create trip
            trip = Trip(
                route_id=request.route_id,
                vehicle_id=request.vehicle_id,
                driver_id=request.driver_id,
                fleet_id=fleet_id,
                created_by=manager_id,
                trip_code=trip_code,
                scheduled_departure=request.scheduled_departure,
                scheduled_arrival=request.scheduled_arrival,
                fare=request.fare,
                total_seats=vehicle.capacity,
                available_seats=vehicle.capacity,
                booked_seats=0,
                notes=request.notes,
            )

            db.add(trip)
            db.commit()
            db.refresh(trip)

            logger.info(f"Trip created: {trip.trip_code} by manager {manager_id}")

            return True, {
                "success": True,
                "message": "Trip created successfully",
                "trip_id": str(trip.id),
                "trip_code": trip.trip_code,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating trip: {str(e)}")
            return False, {"error": f"Failed to create trip: {str(e)}"}

    @staticmethod
    def get_trips(
        fleet_id: str,
        db: Session,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        route_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Get trips with filtering and pagination"""
        try:
            query = db.query(Trip).filter(Trip.fleet_id == fleet_id)

            # Apply filters
            if status:
                query = query.filter(Trip.status == status)
            if route_id:
                query = query.filter(Trip.route_id == route_id)
            if start_date:
                query = query.filter(func.date(Trip.scheduled_departure) >= start_date)
            if end_date:
                query = query.filter(func.date(Trip.scheduled_departure) <= end_date)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            trips = (
                query.order_by(Trip.scheduled_departure.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Format response with related data
            trips_data = []
            for trip in trips:
                # Get route info
                route = db.query(Route).filter(Route.id == trip.route_id).first()

                # Get vehicle info
                vehicle = (
                    db.query(SimpleVehicle)
                    .filter(SimpleVehicle.id == trip.vehicle_id)
                    .first()
                )
                vehicle_info = (
                    f"{vehicle.fleet_number} ({vehicle.license_plate})"
                    if vehicle
                    else "Unknown Vehicle"
                )

                # Get driver info
                driver = (
                    db.query(SimpleDriver)
                    .filter(SimpleDriver.id == trip.driver_id)
                    .first()
                )
                driver_name = (
                    f"Driver {driver.driver_code}" if driver else "Unknown Driver"
                )

                trip_data = {
                    "id": str(trip.id),
                    "route_id": str(trip.route_id),
                    "route_name": route.route_name if route else "Unknown Route",
                    "route_code": route.route_code if route else "Unknown",
                    "origin_name": route.origin_name if route else "Unknown",
                    "destination_name": route.destination_name if route else "Unknown",
                    "vehicle_id": str(trip.vehicle_id),
                    "vehicle_info": vehicle_info,
                    "driver_id": str(trip.driver_id),
                    "driver_name": driver_name,
                    "assignment_id": (
                        str(trip.assignment_id) if trip.assignment_id else None
                    ),
                    "fleet_id": str(trip.fleet_id),
                    "trip_code": trip.trip_code,
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
                    "actual_arrival": (
                        trip.actual_arrival.isoformat() if trip.actual_arrival else None
                    ),
                    "fare": float(trip.fare),
                    "total_seats": trip.total_seats,
                    "available_seats": trip.available_seats,
                    "booked_seats": trip.booked_seats,
                    "status": trip.status,
                    "notes": trip.notes,
                    "cancellation_reason": trip.cancellation_reason,
                    "created_by": str(trip.created_by),
                    "created_at": trip.created_at.isoformat(),
                    "updated_at": trip.updated_at.isoformat(),
                }
                trips_data.append(trip_data)

            total_pages = (total_count + limit - 1) // limit

            return True, {
                "trips": trips_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Error retrieving trips: {str(e)}")
            return False, {"error": f"Failed to retrieve trips: {str(e)}"}

    @staticmethod
    def update_trip(
        trip_id: str,
        fleet_id: str,
        request: TripUpdateRequest,
        manager_id: str,
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Update an existing trip"""
        try:
            trip = (
                db.query(Trip)
                .filter(and_(Trip.id == trip_id, Trip.fleet_id == fleet_id))
                .first()
            )

            if not trip:
                return False, {"error": "Trip not found"}

            # Check if trip can be modified (not completed or cancelled)
            if trip.status in [TripStatus.COMPLETED.value, TripStatus.CANCELLED.value]:
                return False, {"error": "Cannot modify completed or cancelled trips"}

            # If updating vehicle or driver, check availability
            if request.vehicle_id or request.driver_id:
                new_vehicle_id = request.vehicle_id or trip.vehicle_id
                new_driver_id = request.driver_id or trip.driver_id
                new_departure = request.scheduled_departure or trip.scheduled_departure
                new_arrival = (
                    request.scheduled_arrival
                    or trip.scheduled_arrival
                    or (new_departure + timedelta(hours=2))
                )

                availability_request = AvailabilityCheckRequest(
                    vehicle_id=new_vehicle_id,
                    driver_id=new_driver_id,
                    start_datetime=new_departure,
                    end_datetime=new_arrival,
                )

                available, availability_result = TripService.check_availability(
                    fleet_id, availability_request, db
                )
                if not available:
                    return False, {"error": "Failed to check availability"}

                # Filter out the current trip from conflicts
                conflicts = [
                    c
                    for c in availability_result["conflicting_trips"]
                    if c["trip_id"] != str(trip.id)
                ]
                if conflicts:
                    return False, {
                        "error": "Vehicle or driver not available for the updated time",
                        "conflicts": conflicts,
                    }

            # Update fields if provided
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(trip, field, value)

            db.commit()
            db.refresh(trip)

            logger.info(f"Trip updated: {trip.trip_code} by manager {manager_id}")

            return True, {
                "success": True,
                "message": "Trip updated successfully",
                "trip_id": str(trip.id),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating trip: {str(e)}")
            return False, {"error": f"Failed to update trip: {str(e)}"}

    @staticmethod
    def cancel_trip(
        trip_id: str,
        fleet_id: str,
        cancellation_reason: str,
        manager_id: str,
        db: Session,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Cancel a trip"""
        try:
            trip = (
                db.query(Trip)
                .filter(and_(Trip.id == trip_id, Trip.fleet_id == fleet_id))
                .first()
            )

            if not trip:
                return False, {"error": "Trip not found"}

            if trip.status == TripStatus.CANCELLED.value:
                return False, {"error": "Trip is already cancelled"}

            if trip.status == TripStatus.COMPLETED.value:
                return False, {"error": "Cannot cancel completed trip"}

            # Update trip status
            trip.status = TripStatus.CANCELLED.value
            trip.cancellation_reason = cancellation_reason
            trip.available_seats = 0  # No more bookings allowed

            db.commit()
            db.refresh(trip)

            logger.info(f"Trip cancelled: {trip.trip_code} by manager {manager_id}")

            return True, {
                "success": True,
                "message": "Trip cancelled successfully",
                "trip_id": str(trip.id),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling trip: {str(e)}")
            return False, {"error": f"Failed to cancel trip: {str(e)}"}
