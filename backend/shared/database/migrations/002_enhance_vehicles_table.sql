-- Migration: Enhance vehicles table for comprehensive vehicle management
-- Story: 2.1 - Vehicle Registration
-- Date: 2025-01-24

-- Add missing columns to vehicles table
ALTER TABLE vehicles 
ADD COLUMN IF NOT EXISTS manager_id UUID REFERENCES user_profiles(id),
ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS make VARCHAR(100),
ADD COLUMN IF NOT EXISTS model VARCHAR(100),
ADD COLUMN IF NOT EXISTS color VARCHAR(50),
ADD COLUMN IF NOT EXISTS gps_provider VARCHAR(100),
ADD COLUMN IF NOT EXISTS route VARCHAR(200),
ADD COLUMN IF NOT EXISTS registration_date DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS insurance_policy VARCHAR(100),
ADD COLUMN IF NOT EXISTS insurance_expiry DATE,
ADD COLUMN IF NOT EXISTS last_inspection DATE,
ADD COLUMN IF NOT EXISTS next_inspection DATE,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Rename year_manufactured to year for consistency
ALTER TABLE vehicles 
RENAME COLUMN year_manufactured TO year;

-- Update vehicle_status enum to include more statuses
ALTER TYPE vehicle_status ADD VALUE IF NOT EXISTS 'retired';
ALTER TYPE vehicle_status ADD VALUE IF NOT EXISTS 'inspection_due';

-- Add constraints for data integrity
DO $$
BEGIN
    -- Add manager_id foreign key constraint if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicles_manager_id_fkey') THEN
        ALTER TABLE vehicles ADD CONSTRAINT vehicles_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES user_profiles(id);
    END IF;
    
    -- Add year check constraint if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vehicles_year_check') THEN
        ALTER TABLE vehicles ADD CONSTRAINT vehicles_year_check CHECK (year > 1990 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1);
    END IF;
END $$;

-- Create additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_vehicles_manager_id ON vehicles(manager_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_vehicle_type ON vehicles(vehicle_type);
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model ON vehicles(make, model);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_gps_device ON vehicles(gps_device_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_registration_date ON vehicles(registration_date);
CREATE INDEX IF NOT EXISTS idx_vehicles_insurance_expiry ON vehicles(insurance_expiry);
CREATE INDEX IF NOT EXISTS idx_vehicles_next_inspection ON vehicles(next_inspection);

-- Add comments for documentation
COMMENT ON COLUMN vehicles.manager_id IS 'Manager who registered this vehicle';
COMMENT ON COLUMN vehicles.vehicle_type IS 'Type of vehicle: matatu, bus, van, etc.';
COMMENT ON COLUMN vehicles.make IS 'Vehicle manufacturer: Toyota, Nissan, etc.';
COMMENT ON COLUMN vehicles.model IS 'Vehicle model: Hiace, Matatu, etc.';
COMMENT ON COLUMN vehicles.color IS 'Vehicle color';
COMMENT ON COLUMN vehicles.gps_provider IS 'GPS tracking service provider';
COMMENT ON COLUMN vehicles.route IS 'Assigned route if any';
COMMENT ON COLUMN vehicles.registration_date IS 'Date when vehicle was registered in system';
COMMENT ON COLUMN vehicles.insurance_policy IS 'Insurance policy number';
COMMENT ON COLUMN vehicles.insurance_expiry IS 'Insurance expiry date';
COMMENT ON COLUMN vehicles.last_inspection IS 'Date of last vehicle inspection';
COMMENT ON COLUMN vehicles.next_inspection IS 'Date when next inspection is due';
COMMENT ON COLUMN vehicles.is_active IS 'Whether vehicle is active in system';

-- Update existing records to have default values for new fields
UPDATE vehicles 
SET 
    vehicle_type = 'matatu',
    make = 'Unknown',
    model = COALESCE(vehicle_model, 'Unknown'),
    color = 'Unknown',
    is_active = true
WHERE vehicle_type IS NULL;

-- Drop the old vehicle_model column if it exists
ALTER TABLE vehicles DROP COLUMN IF EXISTS vehicle_model;
