# Story 3.2: Passenger Seat Booking

**Epic**: Epic 3 - Booking & Trip Management  
**Story ID**: 3.2  
**Priority**: P0 (Critical)  
**Estimated Effort**: 10 Story Points  
**Status**: 🔄 NOT_STARTED

## 📋 Story Description

**As a passenger, I want to search for available trips and book seats so that I can secure transportation for my journey with confidence and convenience.**

## 🎯 Acceptance Criteria

### ✅ **Trip Discovery**
- [ ] Passenger can search trips by origin, destination, and date
- [ ] System shows real-time seat availability
- [ ] Trip details include departure time, fare, vehicle info, and driver
- [ ] Search results sorted by departure time and relevance
- [ ] Filter options (price range, departure time, vehicle type)

### ✅ **Seat Booking**
- [ ] Passenger can select number of seats to book (1-4 seats max)
- [ ] System prevents overbooking with atomic seat reservation
- [ ] Booking confirmation provided immediately
- [ ] Seat reservation held during payment process (15-minute timeout)
- [ ] Booking details accessible in passenger dashboard

### ✅ **Booking Management**
- [ ] Passenger can view booking history
- [ ] Booking status tracking (pending, confirmed, completed, cancelled)
- [ ] Booking modification (before departure, subject to availability)
- [ ] Booking cancellation with refund policy
- [ ] SMS/Email notifications for booking updates

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Booking status enum
CREATE TYPE booking_status AS ENUM (
    'pending', 'confirmed', 'completed', 'cancelled', 'refunded', 'no_show'
);

-- Bookings table
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    passenger_id UUID NOT NULL REFERENCES user_profiles(id),
    
    -- Booking details
    seats_booked INTEGER NOT NULL CHECK (seats_booked > 0 AND seats_booked <= 4),
    total_amount DECIMAL(10,2) NOT NULL,
    booking_reference VARCHAR(20) UNIQUE NOT NULL,
    
    -- Status and timing
    status booking_status DEFAULT 'pending',
    booking_expires_at TIMESTAMP, -- for pending bookings
    confirmed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    -- Payment information
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    refund_amount DECIMAL(10,2) DEFAULT 0,
    refund_processed_at TIMESTAMP,
    
    -- Contact information
    passenger_phone VARCHAR(20) NOT NULL,
    passenger_email VARCHAR(255),
    emergency_contact VARCHAR(20),
    
    -- Metadata
    booking_source VARCHAR(50) DEFAULT 'web', -- web, mobile, ussd, agent
    special_requests TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_booking_amount CHECK (total_amount > 0),
    CONSTRAINT valid_expiry CHECK (
        booking_expires_at IS NULL OR booking_expires_at > created_at
    )
);

-- Booking history for audit trail
CREATE TABLE booking_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    previous_status booking_status,
    new_status booking_status NOT NULL,
    changed_by UUID REFERENCES user_profiles(id),
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Seat reservations (temporary holds)
CREATE TABLE seat_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    passenger_id UUID NOT NULL REFERENCES user_profiles(id),
    seats_reserved INTEGER NOT NULL,
    reserved_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    booking_id UUID REFERENCES bookings(id),
    
    CONSTRAINT valid_reservation_period CHECK (expires_at > reserved_at)
);

-- Indexes for performance
CREATE INDEX idx_bookings_trip_id ON bookings(trip_id);
CREATE INDEX idx_bookings_passenger_id ON bookings(passenger_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);
CREATE INDEX idx_seat_reservations_trip_expires ON seat_reservations(trip_id, expires_at);

-- Function to generate booking reference
CREATE OR REPLACE FUNCTION generate_booking_reference()
RETURNS VARCHAR(20) AS $$
DECLARE
    ref VARCHAR(20);
BEGIN
    ref := 'BK' || TO_CHAR(NOW(), 'YYMMDD') || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
    RETURN ref;
END;
$$ LANGUAGE plpgsql;
```

### **API Endpoints**
- `GET /api/v1/trips/search` - Search available trips
- `POST /api/v1/bookings/reserve` - Reserve seats (temporary hold)
- `POST /api/v1/bookings/confirm` - Confirm booking with payment
- `GET /api/v1/bookings/user/{user_id}` - Get user bookings
- `GET /api/v1/bookings/{id}` - Get booking details
- `PUT /api/v1/bookings/{id}` - Modify booking
- `DELETE /api/v1/bookings/{id}` - Cancel booking
- `POST /api/v1/bookings/{id}/cancel` - Cancel with reason
- `GET /api/v1/trips/{id}/availability` - Check real-time availability

### **Pydantic Models**
```python
class TripSearchRequest(BaseModel):
    origin: str = Field(..., max_length=255)
    destination: str = Field(..., max_length=255)
    travel_date: date
    passengers: int = Field(1, ge=1, le=4)
    departure_time_from: Optional[time] = None
    departure_time_to: Optional[time] = None
    max_fare: Optional[Decimal] = None

class TripSearchResult(BaseModel):
    id: str
    route_name: str
    origin: str
    destination: str
    scheduled_departure: str
    scheduled_arrival: Optional[str]
    fare: Decimal
    available_seats: int
    vehicle_info: str
    driver_name: str
    estimated_duration: Optional[str]

class SeatReservationRequest(BaseModel):
    trip_id: str
    seats_requested: int = Field(..., ge=1, le=4)
    passenger_phone: str = Field(..., regex=r'^\+254[0-9]{9}$')
    passenger_email: Optional[str] = None

class BookingConfirmRequest(BaseModel):
    reservation_id: str
    payment_method: str = Field(..., regex=r'^(mpesa|card|cash)$')
    payment_reference: Optional[str] = None
    emergency_contact: Optional[str] = None
    special_requests: Optional[str] = Field(None, max_length=500)

class BookingResponse(BaseModel):
    id: str
    booking_reference: str
    trip_details: TripSearchResult
    seats_booked: int
    total_amount: Decimal
    status: str
    passenger_phone: str
    booking_expires_at: Optional[str]
    created_at: str
```

## 🧪 Testing Strategy

### **Unit Tests**
- Trip search functionality
- Seat reservation logic
- Booking confirmation process
- Overbooking prevention
- Booking status transitions

### **Integration Tests**
- End-to-end booking workflow
- Concurrent booking scenarios
- Payment integration
- Notification system
- Real-time availability updates

### **Load Testing**
- Concurrent seat reservations
- High-volume trip searches
- Database performance under load
- API response times
- System stability

## 📊 Definition of Done

- [ ] Trip search system implemented
- [ ] Seat reservation mechanism working
- [ ] Booking confirmation process complete
- [ ] Overbooking prevention verified
- [ ] Booking management functional
- [ ] Real-time availability accurate
- [ ] All tests passing
- [ ] API documentation complete
- [ ] Frontend booking interface ready
- [ ] Performance benchmarks met

## 🔗 Dependencies

- **Prerequisite**: Story 1.1 (Passenger Registration) ✅ COMPLETED
- **Prerequisite**: Story 3.1 (Trip Creation & Scheduling)
- **Payment System**: For booking confirmation
- **Notification System**: SMS/Email for booking updates
- **Database**: PostgreSQL with transaction support

## 🎯 Business Value

- **Revenue Generation**: Enable core booking functionality
- **Customer Experience**: Seamless booking process
- **Inventory Management**: Prevent overbooking
- **Operational Efficiency**: Automated seat management
- **Data Collection**: Customer booking patterns

## 📝 Implementation Notes

- Use database transactions for atomic operations
- Implement seat reservation timeout mechanism
- Add comprehensive logging for audit trail
- Consider Redis for caching search results
- Implement rate limiting for search API
- Add booking reference generation algorithm

---

**Story Owner**: Product Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Passengers, Operations Team, Customer Service
