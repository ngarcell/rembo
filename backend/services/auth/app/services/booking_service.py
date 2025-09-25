"""
Booking Service for Passenger Seat Booking
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from decimal import Decimal
import secrets
import string

from app.models.booking import Booking, Passenger, Payment, BookingStatus, PaymentStatus
from app.models.trip import Trip, Route
from app.models.simple_vehicle import SimpleVehicle
from app.schemas.booking import (
    BookingCreateRequest,
    BookingUpdateRequest,
    PaymentCreateRequest,
    TripSearchRequest,
    PassengerCreateRequest,
)

logger = logging.getLogger(__name__)


class BookingService:
    """Service for booking management"""

    @staticmethod
    def generate_booking_reference() -> str:
        """Generate unique booking reference"""
        # Generate BKG-XXXXXXXX format
        random_part = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return f"BKG-{random_part}"

    @staticmethod
    def generate_payment_reference() -> str:
        """Generate unique payment reference"""
        # Generate PAY-XXXXXXXX format
        random_part = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return f"PAY-{random_part}"

    @staticmethod
    def search_trips(request: TripSearchRequest, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """Search for available trips"""
        try:
            # Build query
            query = db.query(Trip).join(Route).join(SimpleVehicle)

            # Apply filters
            if request.origin:
                query = query.filter(Route.origin.ilike(f"%{request.origin}%"))

            if request.destination:
                query = query.filter(Route.destination.ilike(f"%{request.destination}%"))

            if request.departure_date:
                start_of_day = datetime.combine(request.departure_date, datetime.min.time())
                end_of_day = datetime.combine(request.departure_date, datetime.max.time())
                query = query.filter(
                    and_(
                        Trip.scheduled_departure >= start_of_day,
                        Trip.scheduled_departure <= end_of_day,
                    )
                )

            if request.min_fare:
                query = query.filter(Trip.fare >= request.min_fare)

            if request.max_fare:
                query = query.filter(Trip.fare <= request.max_fare)

            if request.min_seats:
                query = query.filter(Trip.available_seats >= request.min_seats)

            # Only show trips that are scheduled and have available seats
            query = query.filter(
                and_(
                    Trip.status == "scheduled",
                    Trip.available_seats > 0,
                    Trip.scheduled_departure > datetime.utcnow(),
                )
            )

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (request.page - 1) * request.limit
            trips = (
                query.order_by(Trip.scheduled_departure.asc())
                .offset(offset)
                .limit(request.limit)
                .all()
            )

            # Format response
            trips_data = []
            for trip in trips:
                route = db.query(Route).filter(Route.id == trip.route_id).first()
                vehicle = db.query(SimpleVehicle).filter(SimpleVehicle.id == trip.vehicle_id).first()

                trips_data.append({
                    "id": str(trip.id),
                    "route_id": str(trip.route_id),
                    "route_name": route.name if route else "Unknown Route",
                    "origin_name": route.origin if route else "Unknown",
                    "destination_name": route.destination if route else "Unknown",
                    "vehicle_info": f"{vehicle.fleet_number} ({vehicle.license_plate})" if vehicle else "Unknown Vehicle",
                    "driver_name": "Driver Available",  # Simplified for now
                    "scheduled_departure": trip.scheduled_departure.isoformat(),
                    "scheduled_arrival": trip.scheduled_arrival.isoformat() if trip.scheduled_arrival else None,
                    "fare": float(trip.fare),
                    "total_seats": trip.total_seats,
                    "available_seats": trip.available_seats,
                    "status": trip.status,
                })

            total_pages = (total_count + request.limit - 1) // request.limit

            return True, {
                "trips": trips_data,
                "total_count": total_count,
                "page": request.page,
                "limit": request.limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Error searching trips: {str(e)}")
            return False, {"error": f"Failed to search trips: {str(e)}"}

    @staticmethod
    def get_seat_availability(trip_id: str, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """Get seat availability for a trip"""
        try:
            # Get trip details
            trip = db.query(Trip).filter(Trip.id == trip_id).first()
            if not trip:
                return False, {"error": "Trip not found"}

            # Get route details
            route = db.query(Route).filter(Route.id == trip.route_id).first()

            # Get all bookings for this trip
            bookings = db.query(Booking).filter(
                and_(
                    Booking.trip_id == trip_id,
                    Booking.booking_status.in_(["CONFIRMED", "PENDING"])
                )
            ).all()

            # Build seat map
            seat_map = {}
            booked_seats = set()

            for booking in bookings:
                for seat_number in booking.seat_numbers:
                    booked_seats.add(seat_number)
                    seat_map[seat_number] = "booked" if booking.booking_status == "confirmed" else "reserved"

            # Generate available seats (simplified - assuming seats are numbered 1 to total_seats)
            for seat_num in range(1, trip.total_seats + 1):
                seat_number = str(seat_num)
                if seat_number not in booked_seats:
                    seat_map[seat_number] = "available"

            return True, {
                "trip_id": str(trip.id),
                "total_seats": trip.total_seats,
                "available_seats": trip.available_seats,
                "booked_seats": len(booked_seats),
                "seat_map": seat_map,
                "fare": float(trip.fare),
                "route_name": route.name if route else "Unknown Route",
                "departure_time": trip.scheduled_departure.isoformat(),
                "arrival_time": trip.scheduled_arrival.isoformat() if trip.scheduled_arrival else None,
            }

        except Exception as e:
            logger.error(f"Error getting seat availability: {str(e)}")
            return False, {"error": f"Failed to get seat availability: {str(e)}"}

    @staticmethod
    def create_or_get_passenger(request: BookingCreateRequest, db: Session) -> Tuple[bool, Any, Optional[str]]:
        """Create or get existing passenger"""
        try:
            # Check if passenger exists by phone
            existing_passenger = db.query(Passenger).filter(Passenger.phone == request.passenger_phone).first()

            if existing_passenger:
                # Update passenger details if needed
                existing_passenger.first_name = request.passenger_name.split()[0]
                existing_passenger.last_name = " ".join(request.passenger_name.split()[1:]) if len(request.passenger_name.split()) > 1 else ""
                existing_passenger.email = request.passenger_email
                db.commit()
                return True, existing_passenger, None

            # Create new passenger
            name_parts = request.passenger_name.split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            passenger = Passenger(
                first_name=first_name,
                last_name=last_name,
                phone=request.passenger_phone,
                email=request.passenger_email,
            )

            db.add(passenger)
            db.commit()
            db.refresh(passenger)

            logger.info(f"Created new passenger: {passenger.id}")
            return True, passenger, None

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating/getting passenger: {str(e)}")
            return False, None, f"Failed to create/get passenger: {str(e)}"

    @staticmethod
    def create_booking(request: BookingCreateRequest, db: Session) -> Tuple[bool, Dict[str, Any]]:
        """Create a new booking"""
        try:
            # Validate trip exists and has availability
            trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
            if not trip:
                return False, {"error": "Trip not found"}

            if trip.available_seats < request.seats_booked:
                return False, {"error": "Not enough seats available"}

            # Check if requested seats are available
            success, availability_result = BookingService.get_seat_availability(request.trip_id, db)
            if not success:
                return False, {"error": "Failed to check seat availability"}

            seat_map = availability_result["seat_map"]
            for seat_number in request.seat_numbers:
                if seat_map.get(seat_number) != "available":
                    return False, {"error": f"Seat {seat_number} is not available"}

            # Create or get passenger
            success, passenger, error = BookingService.create_or_get_passenger(request, db)
            if not success:
                return False, {"error": error}

            # Generate booking reference
            booking_reference = BookingService.generate_booking_reference()

            # Calculate total fare
            total_fare = trip.fare * request.seats_booked

            # Create booking
            booking = Booking(
                trip_id=request.trip_id,
                passenger_id=passenger.id,
                booking_reference=booking_reference,
                seats_booked=request.seats_booked,
                seat_numbers=request.seat_numbers,
                total_fare=total_fare,
                payment_method=request.payment_method.value if hasattr(request.payment_method, 'value') else str(request.payment_method),
                amount_due=total_fare,
                passenger_name=request.passenger_name,
                passenger_phone=request.passenger_phone,
                passenger_email=request.passenger_email,
                emergency_contact=request.emergency_contact,
                payment_deadline=datetime.utcnow() + timedelta(hours=24),  # 24 hour payment deadline
            )

            db.add(booking)

            # Update trip seat counts
            trip.available_seats -= request.seats_booked

            db.commit()
            db.refresh(booking)

            logger.info(f"Created booking: {booking_reference}")

            return True, {
                "success": True,
                "message": "Booking created successfully",
                "booking_id": str(booking.id),
                "booking_reference": booking_reference,
                "total_fare": float(total_fare),
                "payment_deadline": booking.payment_deadline.isoformat(),
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating booking: {str(e)}")
            return False, {"error": f"Failed to create booking: {str(e)}"}

    @staticmethod
    def get_bookings(passenger_phone: str, page: int = 1, limit: int = 20, db: Session = None) -> Tuple[bool, Dict[str, Any]]:
        """Get bookings for a passenger"""
        try:
            # Get passenger
            passenger = db.query(Passenger).filter(Passenger.phone == passenger_phone).first()
            if not passenger:
                return True, {
                    "bookings": [],
                    "total_count": 0,
                    "page": page,
                    "limit": limit,
                    "total_pages": 0,
                }

            # Build query
            query = db.query(Booking).filter(Booking.passenger_id == passenger.id)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            bookings = (
                query.order_by(Booking.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Format response
            bookings_data = [booking.to_dict() for booking in bookings]
            total_pages = (total_count + limit - 1) // limit

            return True, {
                "bookings": bookings_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Error getting bookings: {str(e)}")
            return False, {"error": f"Failed to get bookings: {str(e)}"}
