-- Migration: Add driver profile fields to drivers table
-- Story: 1.4 - Manager Driver Registration
-- Date: 2025-01-24

-- Add missing columns to drivers table
ALTER TABLE drivers 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS phone VARCHAR(15),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS national_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS license_class VARCHAR(10),
ADD COLUMN IF NOT EXISTS hire_date DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS employment_status VARCHAR(20) DEFAULT 'active',
ADD COLUMN IF NOT EXISTS manager_id UUID;

-- Rename driver_code to driver_id for consistency
ALTER TABLE drivers 
RENAME COLUMN driver_code TO driver_id;

-- Add constraints (PostgreSQL doesn't support IF NOT EXISTS for constraints in older versions)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'drivers_phone_unique') THEN
        ALTER TABLE drivers ADD CONSTRAINT drivers_phone_unique UNIQUE (phone);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'drivers_manager_id_fkey') THEN
        ALTER TABLE drivers ADD CONSTRAINT drivers_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES user_profiles(id);
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_drivers_phone ON drivers(phone);
CREATE INDEX IF NOT EXISTS idx_drivers_manager_id ON drivers(manager_id);
CREATE INDEX IF NOT EXISTS idx_drivers_fleet_id ON drivers(fleet_id);
CREATE INDEX IF NOT EXISTS idx_drivers_driver_id ON drivers(driver_id);

-- Create driver_documents table
CREATE TABLE IF NOT EXISTS driver_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size VARCHAR(20),
    mime_type VARCHAR(100),
    uploaded_by UUID NOT NULL REFERENCES user_profiles(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for driver_documents
CREATE INDEX IF NOT EXISTS idx_driver_documents_driver_id ON driver_documents(driver_id);
CREATE INDEX IF NOT EXISTS idx_driver_documents_type ON driver_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_driver_documents_uploaded_by ON driver_documents(uploaded_by);

-- Update existing drivers table to make required fields NOT NULL
-- (This will only work if there are no existing records or they have values)
-- ALTER TABLE drivers 
-- ALTER COLUMN first_name SET NOT NULL,
-- ALTER COLUMN last_name SET NOT NULL,
-- ALTER COLUMN phone SET NOT NULL,
-- ALTER COLUMN license_class SET NOT NULL,
-- ALTER COLUMN manager_id SET NOT NULL;

-- Add comments for documentation
COMMENT ON TABLE drivers IS 'Driver profiles with personal, license, and employment information';
COMMENT ON COLUMN drivers.driver_id IS 'Unique driver ID in format DRV-XXXYYY';
COMMENT ON COLUMN drivers.manager_id IS 'Manager who registered this driver';
COMMENT ON COLUMN drivers.employment_status IS 'active, inactive, suspended, terminated';

COMMENT ON TABLE driver_documents IS 'Driver document storage metadata';
COMMENT ON COLUMN driver_documents.document_type IS 'license, id_copy, photo, etc.';
COMMENT ON COLUMN driver_documents.file_path IS 'Supabase Storage path';
