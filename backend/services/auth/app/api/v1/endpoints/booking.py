"""
Booking API endpoints for passenger seat booking
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.booking_service import BookingService
from app.schemas.booking import (
    BookingCreateRequest,
    BookingUpdateRequest,
    PaymentCreateRequest,
    TripSearchRequest,
    PassengerCreateRequest,
    BookingResponse,
    PaymentResponse,
    SeatAvailabilityResponse,
    TripSearchListResponse,
    BookingListResponse,
    BookingConfirmationResponse,
    PaymentConfirmationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/trips/search", response_model=TripSearchListResponse)
def search_trips(
    origin: Optional[str] = Query(None, description="Origin city or location"),
    destination: Optional[str] = Query(
        None, description="Destination city or location"
    ),
    departure_date: Optional[str] = Query(
        None, description="Departure date (YYYY-MM-DD)"
    ),
    min_fare: Optional[float] = Query(None, ge=0, description="Minimum fare"),
    max_fare: Optional[float] = Query(None, ge=0, description="Maximum fare"),
    min_seats: Optional[int] = Query(None, ge=1, description="Minimum available seats"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Search for available trips"""
    try:
        # Parse departure_date if provided
        departure_date_obj = None
        if departure_date:
            from datetime import datetime

            departure_date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()

        # Create search request
        search_request = TripSearchRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date_obj,
            min_fare=min_fare,
            max_fare=max_fare,
            min_seats=min_seats,
            page=page,
            limit=limit,
        )

        success, result = BookingService.search_trips(search_request, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to search trips"),
            )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error in search_trips endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/trips/{trip_id}/seats", response_model=SeatAvailabilityResponse)
def get_seat_availability(
    trip_id: str,
    db: Session = Depends(get_db),
):
    """Get seat availability for a specific trip"""
    try:
        success, result = BookingService.get_seat_availability(trip_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Trip not found"),
            )

        return result

    except Exception as e:
        logger.error(f"Error in get_seat_availability endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/bookings", response_model=BookingConfirmationResponse)
def create_booking(
    request: BookingCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new booking"""
    try:
        success, result = BookingService.create_booking(request, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create booking"),
            )

        return result

    except Exception as e:
        logger.error(f"Error in create_booking endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/bookings", response_model=BookingListResponse)
def get_bookings(
    passenger_phone: str = Query(..., description="Passenger phone number"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get bookings for a passenger"""
    try:
        success, result = BookingService.get_bookings(passenger_phone, page, limit, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to get bookings"),
            )

        return result

    except Exception as e:
        logger.error(f"Error in get_bookings endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific booking by ID"""
    try:
        from app.models.booking import Booking

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        return booking.to_dict()

    except Exception as e:
        logger.error(f"Error in get_booking endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    request: BookingUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update a booking (before departure)"""
    try:
        from app.models.booking import Booking
        from datetime import datetime

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Check if booking can be modified
        if booking.booking_status not in ["pending", "confirmed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking cannot be modified in current status",
            )

        # Get trip to check departure time
        from app.models.trip import Trip

        trip = db.query(Trip).filter(Trip.id == booking.trip_id).first()
        if trip and trip.scheduled_departure <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify booking after departure time",
            )

        # Update booking fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)

        db.commit()
        db.refresh(booking)

        return booking.to_dict()

    except Exception as e:
        logger.error(f"Error in update_booking endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Cancel a booking"""
    try:
        from app.models.booking import Booking, BookingStatus
        from app.models.trip import Trip
        from datetime import datetime

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Check if booking can be cancelled
        if booking.booking_status in ["cancelled", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled or completed",
            )

        # Update booking status
        booking.booking_status = BookingStatus.CANCELLED

        # Update trip seat counts
        trip = db.query(Trip).filter(Trip.id == booking.trip_id).first()
        if trip:
            trip.available_seats += booking.seats_booked
            trip.booked_seats -= booking.seats_booked

        db.commit()

        return {"success": True, "message": "Booking cancelled successfully"}

    except Exception as e:
        logger.error(f"Error in cancel_booking endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
