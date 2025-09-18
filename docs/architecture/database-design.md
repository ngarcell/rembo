# Database Design

## Database Schema Overview

The system uses PostgreSQL via Supabase with the following core tables:

### User Management Tables
```sql
-- Users table (managed by Supabase Auth)
users (
  id UUID PRIMARY KEY,
  phone VARCHAR(15) UNIQUE NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User profiles for additional information
user_profiles (
  id UUID PRIMARY KEY REFERENCES users(id),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255),
  is_active BOOLEAN DEFAULT true
);
```

### Fleet Management Tables
```sql
-- Fleet organizations
fleets (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  manager_id UUID REFERENCES users(id),
  fleet_code VARCHAR(10) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Vehicles
vehicles (
  id UUID PRIMARY KEY,
  fleet_id UUID REFERENCES fleets(id),
  fleet_number VARCHAR(20) NOT NULL,
  license_plate VARCHAR(20) UNIQUE NOT NULL,
  capacity INTEGER NOT NULL,
  gps_device_id VARCHAR(100),
  sim_number VARCHAR(20),
  gps_api_key VARCHAR(255) ENCRYPTED,
  status vehicle_status DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Drivers
drivers (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  driver_code VARCHAR(20) UNIQUE NOT NULL,
  license_number VARCHAR(50) NOT NULL,
  fleet_id UUID REFERENCES fleets(id),
  is_active BOOLEAN DEFAULT true
);

-- Vehicle assignments
vehicle_assignments (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  driver_id UUID REFERENCES drivers(id),
  assigned_at TIMESTAMP DEFAULT NOW(),
  unassigned_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);
```

### Booking & Trip Tables
```sql
-- Routes
routes (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  origin VARCHAR(255) NOT NULL,
  destination VARCHAR(255) NOT NULL,
  distance_km DECIMAL(8,2),
  estimated_duration_minutes INTEGER,
  base_fare DECIMAL(10,2) NOT NULL
);

-- Trips
trips (
  id UUID PRIMARY KEY,
  route_id UUID REFERENCES routes(id),
  vehicle_id UUID REFERENCES vehicles(id),
  driver_id UUID REFERENCES drivers(id),
  scheduled_departure TIMESTAMP NOT NULL,
  actual_departure TIMESTAMP,
  scheduled_arrival TIMESTAMP,
  actual_arrival TIMESTAMP,
  status trip_status DEFAULT 'scheduled',
  fare DECIMAL(10,2) NOT NULL,
  available_seats INTEGER NOT NULL
);

-- Bookings
bookings (
  id UUID PRIMARY KEY,
  trip_id UUID REFERENCES trips(id),
  passenger_id UUID REFERENCES users(id),
  seats_booked INTEGER NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  booking_status booking_status DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Payment Tables
```sql
-- Payments
payments (
  id UUID PRIMARY KEY,
  booking_id UUID REFERENCES bookings(id),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'KES',
  payment_method VARCHAR(50) DEFAULT 'mpesa',
  mpesa_transaction_id VARCHAR(100),
  status payment_status DEFAULT 'pending',
  initiated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Payment receipts
receipts (
  id UUID PRIMARY KEY,
  payment_id UUID REFERENCES payments(id),
  receipt_number VARCHAR(50) UNIQUE NOT NULL,
  receipt_data JSONB NOT NULL,
  generated_at TIMESTAMP DEFAULT NOW()
);
```

### GPS & Location Tables
```sql
-- GPS locations
gps_locations (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  altitude DECIMAL(8, 2),
  speed DECIMAL(5, 2),
  heading DECIMAL(5, 2),
  accuracy DECIMAL(5, 2),
  recorded_at TIMESTAMP NOT NULL,
  received_at TIMESTAMP DEFAULT NOW()
);

-- Location history (partitioned by date)
location_history (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  trip_id UUID REFERENCES trips(id),
  route_data JSONB NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  total_distance_km DECIMAL(8, 2),
  created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);
```

## Database Optimization

### Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_vehicles_fleet_id ON vehicles(fleet_id);
CREATE INDEX idx_trips_vehicle_date ON trips(vehicle_id, scheduled_departure);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_gps_vehicle_time ON gps_locations(vehicle_id, recorded_at DESC);
CREATE INDEX idx_payments_booking ON payments(booking_id);

-- Composite indexes for common queries
CREATE INDEX idx_trips_route_status_date ON trips(route_id, status, scheduled_departure);
CREATE INDEX idx_bookings_trip_status ON bookings(trip_id, booking_status);
```

### Row Level Security (RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Example policies
CREATE POLICY "Managers can view their fleet vehicles" ON vehicles
  FOR SELECT USING (
    fleet_id IN (
      SELECT id FROM fleets WHERE manager_id = auth.uid()
    )
  );

CREATE POLICY "Passengers can view their bookings" ON bookings
  FOR SELECT USING (passenger_id = auth.uid());
```
