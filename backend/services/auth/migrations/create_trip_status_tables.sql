-- Migration: Create Trip Status Tracking Tables
-- Description: Add real-time trip status tracking, GPS locations, and notification preferences

-- Create trip status enum
CREATE TYPE trip_status_enum AS ENUM (
    'scheduled', 'departed', 'in_transit', 'arrived', 'completed', 'cancelled', 'delayed'
);

-- Create update source enum
CREATE TYPE update_source_enum AS ENUM (
    'system', 'driver', 'gps', 'manual', 'passenger'
);

-- Trip status updates table
CREATE TABLE trip_status_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    status trip_status_enum NOT NULL,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_name VARCHAR(255),
    estimated_arrival TIMESTAMP WITH TIME ZONE,
    delay_minutes INTEGER DEFAULT 0 NOT NULL,
    update_source update_source_enum DEFAULT 'system' NOT NULL,
    notes TEXT,
    updated_by UUID REFERENCES user_profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for trip_status_updates
CREATE INDEX idx_trip_status_updates_trip_id ON trip_status_updates(trip_id);
CREATE INDEX idx_trip_status_updates_created_at ON trip_status_updates(created_at);
CREATE INDEX idx_trip_status_updates_status ON trip_status_updates(status);

-- Update existing gps_locations table if it doesn't have all required columns
-- First check if the table exists and has the right structure
DO $$
BEGIN
    -- Add trip_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'trip_id'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN trip_id UUID REFERENCES trips(id) ON DELETE SET NULL;
        CREATE INDEX idx_gps_locations_trip_id ON gps_locations(trip_id);
    END IF;
    
    -- Add altitude column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'altitude'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN altitude DECIMAL(8, 2);
    END IF;
    
    -- Add speed_kmh column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'speed_kmh'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN speed_kmh DECIMAL(5, 2);
    END IF;
    
    -- Add heading column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'heading'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN heading DECIMAL(5, 2);
    END IF;
    
    -- Add accuracy_meters column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'accuracy_meters'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN accuracy_meters INTEGER;
    END IF;
    
    -- Add recorded_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'recorded_at'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
    END IF;
    
    -- Add received_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'gps_locations' AND column_name = 'received_at'
    ) THEN
        ALTER TABLE gps_locations ADD COLUMN received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
    END IF;
END $$;

-- Create additional indexes for gps_locations if they don't exist
CREATE INDEX IF NOT EXISTS idx_gps_locations_vehicle_recorded_at ON gps_locations(vehicle_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_gps_locations_recorded_at ON gps_locations(recorded_at);

-- Notification preferences table
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES user_profiles(id) ON DELETE CASCADE,
    sms_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    push_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    trip_status_updates BOOLEAN DEFAULT TRUE NOT NULL,
    delay_notifications BOOLEAN DEFAULT TRUE NOT NULL,
    cancellation_alerts BOOLEAN DEFAULT TRUE NOT NULL,
    booking_confirmations BOOLEAN DEFAULT TRUE NOT NULL,
    advance_notice_minutes INTEGER DEFAULT 30 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for notification_preferences
CREATE INDEX idx_notification_preferences_user_id ON notification_preferences(user_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_notification_preferences_updated_at 
    BEFORE UPDATE ON notification_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default notification preferences for existing users
INSERT INTO notification_preferences (user_id)
SELECT id FROM user_profiles 
WHERE id NOT IN (SELECT user_id FROM notification_preferences);

-- Add comments for documentation
COMMENT ON TABLE trip_status_updates IS 'Real-time trip status updates and tracking history';
COMMENT ON TABLE notification_preferences IS 'User preferences for notifications and alerts';
COMMENT ON COLUMN trip_status_updates.delay_minutes IS 'Delay in minutes from scheduled time';
COMMENT ON COLUMN trip_status_updates.update_source IS 'Source of the status update (system, driver, gps, manual, passenger)';
COMMENT ON COLUMN gps_locations.heading IS 'Compass heading in degrees (0-360)';
COMMENT ON COLUMN gps_locations.accuracy_meters IS 'GPS accuracy in meters';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON trip_status_updates TO matatu_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON notification_preferences TO matatu_app_user;
