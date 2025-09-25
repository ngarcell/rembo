"""
Pydantic schemas for booking system
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.booking import (
    BookingStatus,
    PaymentStatus,
    PaymentMethod,
    SeatPreference,
)


# Request Schemas
class PassengerCreateRequest(BaseModel):
    """Request schema for creating a passenger"""

    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+254[0-9]{9}$")
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = Field(None, max_length=50)
    preferred_seat_type: SeatPreference = SeatPreference.ANY

    @validator("phone")
    def validate_phone(cls, v):
        if not v.startswith("+254"):
            raise ValueError("Phone number must be in Kenyan format (+254XXXXXXXXX)")
        return v


class BookingCreateRequest(BaseModel):
    """Request schema for creating a booking"""

    trip_id: str = Field(..., description="Trip ID to book")
    seats_booked: int = Field(..., ge=1, le=10, description="Number of seats to book")
    seat_numbers: List[str] = Field(..., min_items=1, max_items=10)
    passenger_name: str = Field(..., min_length=2, max_length=200)
    passenger_phone: str = Field(..., pattern=r"^\+254[0-9]{9}$")
    passenger_email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    emergency_contact: Optional[str] = Field(None, pattern=r"^\+254[0-9]{9}$")
    payment_method: PaymentMethod

    @validator("seat_numbers")
    def validate_seat_numbers(cls, v, values):
        if "seats_booked" in values and len(v) != values["seats_booked"]:
            raise ValueError("Number of seat numbers must match seats_booked")
        return v

    @validator("passenger_phone", "emergency_contact")
    def validate_phone_format(cls, v):
        if v and not v.startswith("+254"):
            raise ValueError("Phone number must be in Kenyan format (+254XXXXXXXXX)")
        return v


class BookingUpdateRequest(BaseModel):
    """Request schema for updating a booking"""

    seats_booked: Optional[int] = Field(None, ge=1, le=10)
    seat_numbers: Optional[List[str]] = Field(None, min_items=1, max_items=10)
    passenger_name: Optional[str] = Field(None, min_length=2, max_length=200)
    passenger_phone: Optional[str] = Field(None, pattern=r"^\+254[0-9]{9}$")
    passenger_email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    emergency_contact: Optional[str] = Field(None, pattern=r"^\+254[0-9]{9}$")
    payment_method: Optional[PaymentMethod] = None

    @validator("seat_numbers")
    def validate_seat_numbers(cls, v, values):
        if v and "seats_booked" in values and values["seats_booked"]:
            if len(v) != values["seats_booked"]:
                raise ValueError("Number of seat numbers must match seats_booked")
        return v


class PaymentCreateRequest(BaseModel):
    """Request schema for creating a payment"""

    booking_id: str = Field(..., description="Booking ID to pay for")
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    payment_method: PaymentMethod
    gateway_transaction_id: Optional[str] = Field(None, max_length=100)

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        return v


class TripSearchRequest(BaseModel):
    """Request schema for searching trips"""

    origin: Optional[str] = Field(None, min_length=2, max_length=100)
    destination: Optional[str] = Field(None, min_length=2, max_length=100)
    departure_date: Optional[date] = None
    min_fare: Optional[Decimal] = Field(None, ge=0)
    max_fare: Optional[Decimal] = Field(None, ge=0)
    min_seats: Optional[int] = Field(None, ge=1)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    @validator("max_fare")
    def validate_fare_range(cls, v, values):
        if v and "min_fare" in values and values["min_fare"]:
            if v < values["min_fare"]:
                raise ValueError("max_fare must be greater than or equal to min_fare")
        return v


# Response Schemas
class PassengerResponse(BaseModel):
    """Response schema for passenger data"""

    id: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_id: Optional[str] = None
    preferred_seat_type: str
    loyalty_points: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Response schema for booking data"""

    id: str
    trip_id: str
    passenger_id: str
    booking_reference: str
    seats_booked: int
    seat_numbers: List[str]
    total_fare: float
    booking_status: str
    payment_method: Optional[str] = None
    payment_status: str
    amount_paid: float
    amount_due: float
    passenger_name: str
    passenger_phone: str
    passenger_email: Optional[str] = None
    emergency_contact: Optional[str] = None
    booking_date: str
    payment_deadline: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Response schema for payment data"""

    id: str
    booking_id: str
    payment_reference: str
    payment_method: str
    amount: float
    currency: str
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[str] = None
    payment_status: str
    processed_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SeatAvailabilityResponse(BaseModel):
    """Response schema for seat availability"""

    trip_id: str
    total_seats: int
    available_seats: int
    booked_seats: int
    seat_map: Dict[str, str]  # seat_number -> status ('available', 'booked', 'reserved')
    fare: float
    route_name: str
    departure_time: str
    arrival_time: Optional[str] = None

    class Config:
        from_attributes = True


class TripSearchResponse(BaseModel):
    """Response schema for trip search results"""

    id: str
    route_id: str
    route_name: str
    origin_name: str
    destination_name: str
    vehicle_info: str
    driver_name: str
    scheduled_departure: str
    scheduled_arrival: Optional[str] = None
    fare: float
    total_seats: int
    available_seats: int
    status: str

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Response schema for booking list"""

    bookings: List[BookingResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True


class TripSearchListResponse(BaseModel):
    """Response schema for trip search list"""

    trips: List[TripSearchResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True


# Utility Schemas
class BookingConfirmationResponse(BaseModel):
    """Response schema for booking confirmation"""

    success: bool
    message: str
    booking_id: str
    booking_reference: str
    total_fare: float
    payment_deadline: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentConfirmationResponse(BaseModel):
    """Response schema for payment confirmation"""

    success: bool
    message: str
    payment_id: str
    payment_reference: str
    amount: float
    payment_status: str

    class Config:
        from_attributes = True
