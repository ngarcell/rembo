-- Matatu Fleet Management Database Schema
-- Based on architecture document specifications

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'passenger');
CREATE TYPE vehicle_status AS ENUM ('active', 'maintenance', 'inactive');
CREATE TYPE trip_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');

-- Users table (extends Supabase auth.users)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL, -- References auth.users(id)
    phone VARCHAR(15) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    role user_role NOT NULL DEFAULT 'passenger',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Fleet organizations
CREATE TABLE fleets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    manager_id UUID REFERENCES user_profiles(id),
    fleet_code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicles
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID REFERENCES fleets(id),
    fleet_number VARCHAR(20) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    vehicle_model VARCHAR(100),
    year_manufactured INTEGER,
    gps_device_id VARCHAR(100),
    sim_number VARCHAR(20),
    gps_api_key TEXT, -- Encrypted in application layer
    status vehicle_status DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(fleet_id, fleet_number)
);

-- Drivers
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id),
    driver_code VARCHAR(20) UNIQUE NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    license_expiry DATE,
    fleet_id UUID REFERENCES fleets(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle assignments
CREATE TABLE vehicle_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    manager_id UUID NOT NULL REFERENCES user_profiles(id),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    unassigned_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    assignment_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add partial unique constraints for active assignments
CREATE UNIQUE INDEX idx_vehicle_assignments_active_vehicle_unique
ON vehicle_assignments(vehicle_id) WHERE is_active = true;

CREATE UNIQUE INDEX idx_vehicle_assignments_active_driver_unique
ON vehicle_assignments(driver_id) WHERE is_active = true;

-- Add indexes for performance
CREATE INDEX idx_vehicle_assignments_vehicle_id ON vehicle_assignments(vehicle_id);
CREATE INDEX idx_vehicle_assignments_driver_id ON vehicle_assignments(driver_id);
CREATE INDEX idx_vehicle_assignments_fleet_id ON vehicle_assignments(fleet_id);
CREATE INDEX idx_vehicle_assignments_manager_id ON vehicle_assignments(manager_id);
CREATE INDEX idx_vehicle_assignments_active ON vehicle_assignments(is_active) WHERE is_active = true;

-- Vehicle status history
CREATE TABLE vehicle_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_by UUID NOT NULL REFERENCES user_profiles(id),
    reason TEXT,
    notes TEXT,
    changed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_date TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    assigned_to VARCHAR(200),
    performed_by VARCHAR(200),
    created_by UUID NOT NULL REFERENCES user_profiles(id),
    estimated_cost INTEGER,
    actual_cost INTEGER,
    is_completed BOOLEAN DEFAULT false,
    is_approved BOOLEAN DEFAULT false,
    odometer_reading INTEGER,
    next_service_km INTEGER,
    next_service_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle documents
CREATE TABLE vehicle_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    document_number VARCHAR(100),
    issuer VARCHAR(200),
    issued_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT true,
    is_expired BOOLEAN DEFAULT false,
    file_path VARCHAR(500),
    file_name VARCHAR(200),
    notes TEXT,
    uploaded_by UUID NOT NULL REFERENCES user_profiles(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle inspections
CREATE TABLE vehicle_inspections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    inspection_type VARCHAR(100) NOT NULL,
    inspector_name VARCHAR(200),
    inspection_station VARCHAR(200),
    passed BOOLEAN,
    score INTEGER,
    inspection_date TIMESTAMP NOT NULL,
    next_inspection_date TIMESTAMP,
    findings TEXT,
    recommendations TEXT,
    certificate_number VARCHAR(100),
    odometer_reading INTEGER,
    created_by UUID NOT NULL REFERENCES user_profiles(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for vehicle status tables
CREATE INDEX idx_vehicle_status_history_vehicle_id ON vehicle_status_history(vehicle_id);
CREATE INDEX idx_vehicle_status_history_changed_at ON vehicle_status_history(changed_at);
CREATE INDEX idx_maintenance_records_vehicle_id ON maintenance_records(vehicle_id);
CREATE INDEX idx_maintenance_records_priority ON maintenance_records(priority);
CREATE INDEX idx_maintenance_records_completed ON maintenance_records(is_completed);
CREATE INDEX idx_vehicle_documents_vehicle_id ON vehicle_documents(vehicle_id);
CREATE INDEX idx_vehicle_documents_type ON vehicle_documents(document_type);
CREATE INDEX idx_vehicle_documents_expiry ON vehicle_documents(expiry_date);
CREATE INDEX idx_vehicle_inspections_vehicle_id ON vehicle_inspections(vehicle_id);
CREATE INDEX idx_vehicle_inspections_date ON vehicle_inspections(inspection_date);

-- Routes
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    distance_km DECIMAL(8,2),
    estimated_duration_minutes INTEGER,
    base_fare DECIMAL(10,2) NOT NULL CHECK (base_fare >= 0),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trips
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id UUID REFERENCES routes(id),
    vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES drivers(id),
    scheduled_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    scheduled_arrival TIMESTAMP,
    actual_arrival TIMESTAMP,
    status trip_status DEFAULT 'scheduled',
    fare DECIMAL(10,2) NOT NULL CHECK (fare >= 0),
    available_seats INTEGER NOT NULL CHECK (available_seats >= 0),
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CHECK (available_seats <= total_seats)
);

-- Bookings
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID REFERENCES trips(id),
    passenger_id UUID REFERENCES user_profiles(id),
    seats_booked INTEGER NOT NULL CHECK (seats_booked > 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    booking_status booking_status DEFAULT 'pending',
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    currency VARCHAR(3) DEFAULT 'KES',
    payment_method VARCHAR(50) DEFAULT 'mpesa',
    mpesa_transaction_id VARCHAR(100),
    mpesa_checkout_request_id VARCHAR(100),
    status payment_status DEFAULT 'pending',
    initiated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payment receipts
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID REFERENCES payments(id),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- GPS locations
CREATE TABLE gps_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Create indexes for performance
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_phone ON user_profiles(phone);
CREATE INDEX idx_vehicles_fleet_id ON vehicles(fleet_id);
CREATE INDEX idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX idx_drivers_fleet_id ON drivers(fleet_id);
CREATE INDEX idx_vehicle_assignments_vehicle_id ON vehicle_assignments(vehicle_id);
CREATE INDEX idx_vehicle_assignments_driver_id ON vehicle_assignments(driver_id);
CREATE INDEX idx_trips_vehicle_date ON trips(vehicle_id, scheduled_departure);
CREATE INDEX idx_trips_route_status_date ON trips(route_id, status, scheduled_departure);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_bookings_trip_status ON bookings(trip_id, booking_status);
CREATE INDEX idx_payments_booking ON payments(booking_id);
CREATE INDEX idx_gps_vehicle_time ON gps_locations(vehicle_id, recorded_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fleets_updated_at BEFORE UPDATE ON fleets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_drivers_updated_at BEFORE UPDATE ON drivers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Performance metrics table
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE, -- NULL for fleet-wide metrics
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- fuel_efficiency, revenue, passenger_count, etc.
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(20), -- km, liters, KES, hours, etc.

    -- Time period
    date_recorded DATE NOT NULL,
    period_start TIMESTAMP,
    period_end TIMESTAMP,

    -- Context
    route_id VARCHAR(100),
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,

    -- Additional data
    notes TEXT,
    recorded_by UUID NOT NULL REFERENCES user_profiles(id),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Route performance table
CREATE TABLE route_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,
    route_name VARCHAR(200) NOT NULL,
    route_code VARCHAR(50),

    -- Performance metrics
    total_trips INTEGER DEFAULT 0 NOT NULL,
    total_distance_km DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
    total_revenue INTEGER DEFAULT 0 NOT NULL, -- In cents
    total_passengers INTEGER DEFAULT 0 NOT NULL,
    average_trip_time_minutes DECIMAL(8,2),
    on_time_percentage DECIMAL(5,2),

    -- Efficiency metrics
    fuel_consumption_liters DECIMAL(10,2),
    fuel_efficiency_km_per_liter DECIMAL(8,2),
    maintenance_cost INTEGER DEFAULT 0 NOT NULL, -- In cents

    -- Time period
    date_recorded DATE NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,

    -- Metadata
    recorded_by UUID NOT NULL REFERENCES user_profiles(id),
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle performance summary table
CREATE TABLE vehicle_performance_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,

    -- Summary period
    summary_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly

    -- Operational metrics
    trips_completed INTEGER DEFAULT 0 NOT NULL,
    total_distance_km DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
    total_revenue INTEGER DEFAULT 0 NOT NULL, -- In cents
    total_passengers INTEGER DEFAULT 0 NOT NULL,
    active_hours DECIMAL(8,2) DEFAULT 0.0 NOT NULL,

    -- Efficiency metrics
    fuel_consumed_liters DECIMAL(10,2),
    fuel_cost INTEGER, -- In cents
    maintenance_cost INTEGER DEFAULT 0 NOT NULL, -- In cents
    utilization_rate DECIMAL(5,2), -- Percentage

    -- Performance indicators
    average_speed_kmh DECIMAL(8,2),
    on_time_trips INTEGER DEFAULT 0 NOT NULL,
    delayed_trips INTEGER DEFAULT 0 NOT NULL,
    cancelled_trips INTEGER DEFAULT 0 NOT NULL,

    -- Financial metrics
    gross_revenue INTEGER DEFAULT 0 NOT NULL, -- In cents
    operating_cost INTEGER DEFAULT 0 NOT NULL, -- In cents
    net_profit INTEGER DEFAULT 0 NOT NULL, -- In cents
    profit_margin DECIMAL(5,2), -- Percentage

    -- Driver assignment
    primary_driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Fleet KPIs table
CREATE TABLE fleet_kpis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,

    -- KPI identification
    kpi_name VARCHAR(100) NOT NULL,
    kpi_category VARCHAR(50) NOT NULL, -- operational, financial, safety, etc.

    -- Values
    current_value DECIMAL(15,2) NOT NULL,
    target_value DECIMAL(15,2),
    previous_value DECIMAL(15,2),

    -- Performance
    achievement_percentage DECIMAL(5,2),
    trend VARCHAR(20), -- improving, declining, stable

    -- Time period
    measurement_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly

    -- Metadata
    unit VARCHAR(20),
    description TEXT,
    calculation_method TEXT,

    recorded_by UUID NOT NULL REFERENCES user_profiles(id),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for analytics tables
CREATE INDEX idx_performance_metrics_vehicle_id ON performance_metrics(vehicle_id);
CREATE INDEX idx_performance_metrics_fleet_id ON performance_metrics(fleet_id);
CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(date_recorded);
CREATE INDEX idx_performance_metrics_route ON performance_metrics(route_id);

CREATE INDEX idx_route_performance_fleet_id ON route_performance(fleet_id);
CREATE INDEX idx_route_performance_route_name ON route_performance(route_name);
CREATE INDEX idx_route_performance_route_code ON route_performance(route_code);
CREATE INDEX idx_route_performance_date ON route_performance(date_recorded);

CREATE INDEX idx_vehicle_performance_summary_vehicle_id ON vehicle_performance_summary(vehicle_id);
CREATE INDEX idx_vehicle_performance_summary_fleet_id ON vehicle_performance_summary(fleet_id);
CREATE INDEX idx_vehicle_performance_summary_date ON vehicle_performance_summary(summary_date);
CREATE INDEX idx_vehicle_performance_summary_period ON vehicle_performance_summary(period_type);

CREATE INDEX idx_fleet_kpis_fleet_id ON fleet_kpis(fleet_id);
CREATE INDEX idx_fleet_kpis_name ON fleet_kpis(kpi_name);
CREATE INDEX idx_fleet_kpis_category ON fleet_kpis(kpi_category);
CREATE INDEX idx_fleet_kpis_date ON fleet_kpis(measurement_date);

-- Add updated_at triggers for analytics tables
CREATE TRIGGER update_performance_metrics_updated_at BEFORE UPDATE ON performance_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_route_performance_updated_at BEFORE UPDATE ON route_performance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vehicle_performance_summary_updated_at BEFORE UPDATE ON vehicle_performance_summary FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fleet_kpis_updated_at BEFORE UPDATE ON fleet_kpis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ENHANCED TRIP MANAGEMENT SYSTEM (Story 3.1)
-- =====================================================

-- Drop existing basic tables to replace with enhanced versions
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS routes CASCADE;

-- Enhanced routes table for comprehensive trip planning
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,

    -- Route Information
    route_code VARCHAR(20) NOT NULL,
    route_name VARCHAR(255) NOT NULL,
    origin_name VARCHAR(255) NOT NULL,
    destination_name VARCHAR(255) NOT NULL,

    -- Route Details
    distance_km DECIMAL(8,2),
    estimated_duration_minutes INTEGER,
    base_fare DECIMAL(10,2) NOT NULL CHECK (base_fare >= 0),

    -- Optional route data
    waypoints TEXT, -- JSON string of waypoints
    description TEXT,

    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(fleet_id, route_code)
);

-- Enhanced trips table for comprehensive trip management
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES vehicle_assignments(id) ON DELETE SET NULL,
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES user_profiles(id),

    -- Trip Code
    trip_code VARCHAR(50) NOT NULL UNIQUE,

    -- Schedule Information
    scheduled_departure TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_arrival TIMESTAMP WITH TIME ZONE,
    actual_departure TIMESTAMP WITH TIME ZONE,
    actual_arrival TIMESTAMP WITH TIME ZONE,

    -- Trip Details
    fare DECIMAL(10,2) NOT NULL CHECK (fare >= 0),
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    available_seats INTEGER NOT NULL CHECK (available_seats >= 0),
    booked_seats INTEGER DEFAULT 0 NOT NULL CHECK (booked_seats >= 0),

    -- Status and Notes
    status trip_status DEFAULT 'scheduled' NOT NULL,
    notes TEXT,
    cancellation_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_trip_times CHECK (
        scheduled_arrival IS NULL OR scheduled_arrival > scheduled_departure
    ),
    CONSTRAINT valid_actual_times CHECK (
        actual_arrival IS NULL OR actual_departure IS NULL OR actual_arrival >= actual_departure
    ),
    CONSTRAINT valid_seat_count CHECK (available_seats <= total_seats),
    CONSTRAINT valid_booked_seats CHECK (booked_seats <= total_seats),
    CONSTRAINT seat_count_consistency CHECK (available_seats + booked_seats = total_seats)
);

-- Trip templates for recurring trip scheduling
CREATE TABLE trip_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    fleet_id UUID NOT NULL REFERENCES fleets(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES user_profiles(id),

    -- Template Information
    template_name VARCHAR(255) NOT NULL,
    departure_time TIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL CHECK (fare >= 0),

    -- Recurrence Pattern
    days_of_week INTEGER[] NOT NULL, -- [1,2,3,4,5] for weekdays

    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for enhanced routes
CREATE INDEX idx_routes_fleet_id ON routes(fleet_id);
CREATE INDEX idx_routes_route_code ON routes(route_code);
CREATE INDEX idx_routes_is_active ON routes(is_active);
CREATE INDEX idx_routes_origin_destination ON routes(origin_name, destination_name);

-- Create indexes for enhanced trips
CREATE INDEX idx_trips_route_date ON trips(route_id, scheduled_departure);
CREATE INDEX idx_trips_vehicle_date ON trips(vehicle_id, scheduled_departure);
CREATE INDEX idx_trips_driver_date ON trips(driver_id, scheduled_departure);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_fleet_date ON trips(fleet_id, scheduled_departure);
CREATE INDEX idx_trips_trip_code ON trips(trip_code);
CREATE INDEX idx_trips_departure_date ON trips(DATE(scheduled_departure));

-- Create indexes for trip_templates
CREATE INDEX idx_trip_templates_route_id ON trip_templates(route_id);
CREATE INDEX idx_trip_templates_fleet_id ON trip_templates(fleet_id);
CREATE INDEX idx_trip_templates_is_active ON trip_templates(is_active);
CREATE INDEX idx_trip_templates_days_of_week ON trip_templates USING GIN(days_of_week);

-- Add updated_at triggers for trip management tables
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trip_templates_updated_at BEFORE UPDATE ON trip_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
