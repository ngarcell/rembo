-- Drop existing bookings table and recreate with correct schema
DROP TABLE IF EXISTS bookings CASCADE;

-- Create enhanced bookings table
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    passenger_id UUID NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
    booking_reference VARCHAR(20) UNIQUE NOT NULL,

    -- Booking Details
    seats_booked INTEGER NOT NULL CHECK (seats_booked > 0),
    seat_numbers TEXT[], -- Array of seat numbers
    total_fare DECIMAL(10,2) NOT NULL CHECK (total_fare > 0),
    booking_status booking_status NOT NULL DEFAULT 'pending',

    -- Payment Details
    payment_method payment_method,
    payment_status payment_status NOT NULL DEFAULT 'pending',
    amount_paid DECIMAL(10,2) DEFAULT 0.00 CHECK (amount_paid >= 0),
    amount_due DECIMAL(10,2) NOT NULL CHECK (amount_due >= 0),

    -- Passenger Details (denormalized for quick access)
    passenger_name VARCHAR(200) NOT NULL,
    passenger_phone VARCHAR(15) NOT NULL,
    passenger_email VARCHAR(255),
    emergency_contact VARCHAR(15),

    -- Timestamps
    booking_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    payment_deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CHECK (amount_paid <= total_fare),
    CHECK (amount_due <= total_fare)
);

-- Create indexes
CREATE INDEX idx_bookings_trip_id ON bookings(trip_id);
CREATE INDEX idx_bookings_passenger_id ON bookings(passenger_id);
CREATE INDEX idx_bookings_status ON bookings(booking_status);
CREATE INDEX idx_bookings_phone ON bookings(passenger_phone);
