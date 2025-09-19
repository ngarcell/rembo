-- Supabase Database Schema for Matatu Fleet Management System
-- This script sets up the necessary tables and RLS policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user role enum type
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'passenger');

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL, -- References auth.users.id
    phone VARCHAR(15) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    role user_role NOT NULL DEFAULT 'passenger',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_phone ON profiles(phone);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Service role can insert profiles (for registration)
CREATE POLICY "Service role can insert profiles" ON profiles
    FOR INSERT WITH CHECK (true);

-- Policy: Service role can view all profiles (for admin operations)
CREATE POLICY "Service role can view all profiles" ON profiles
    FOR SELECT USING (true);

-- Policy: Service role can update all profiles (for admin operations)
CREATE POLICY "Service role can update all profiles" ON profiles
    FOR UPDATE USING (true);

-- Policy: Admins can view all profiles
CREATE POLICY "Admins can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles p 
            WHERE p.user_id = auth.uid() 
            AND p.role = 'admin'
        )
    );

-- Policy: Admins can update all profiles
CREATE POLICY "Admins can update all profiles" ON profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles p 
            WHERE p.user_id = auth.uid() 
            AND p.role = 'admin'
        )
    );

-- Create a function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- This function can be used to automatically create a profile
    -- when a new user is created in auth.users
    -- For now, we'll handle this in the application layer
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Optional: Create trigger for automatic profile creation
-- DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
-- CREATE TRIGGER on_auth_user_created
--     AFTER INSERT ON auth.users
--     FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON profiles TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Insert sample data (optional - for testing)
-- INSERT INTO profiles (user_id, phone, first_name, last_name, email, role) VALUES
-- (uuid_generate_v4(), '+254700000001', 'John', 'Doe', 'john@example.com', 'passenger'),
-- (uuid_generate_v4(), '+254700000002', 'Jane', 'Smith', 'jane@example.com', 'admin');

-- Create a view for user profiles with additional computed fields
CREATE OR REPLACE VIEW user_profiles_view AS
SELECT 
    p.*,
    CONCAT(p.first_name, ' ', p.last_name) as full_name,
    CASE 
        WHEN p.first_name IS NOT NULL THEN p.first_name
        ELSE SPLIT_PART(p.phone, '+254', 2)
    END as display_name
FROM profiles p;

-- Grant access to the view
GRANT SELECT ON user_profiles_view TO anon, authenticated;

-- Create function to get user profile by phone
CREATE OR REPLACE FUNCTION get_profile_by_phone(phone_number TEXT)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    phone VARCHAR(15),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    role user_role,
    is_active BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.user_id, p.phone, p.first_name, p.last_name, 
           p.email, p.role, p.is_active, p.created_at, p.updated_at
    FROM profiles p
    WHERE p.phone = phone_number;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION get_profile_by_phone(TEXT) TO anon, authenticated;

-- Create function to update user profile
CREATE OR REPLACE FUNCTION update_user_profile(
    profile_user_id UUID,
    new_first_name VARCHAR(100) DEFAULT NULL,
    new_last_name VARCHAR(100) DEFAULT NULL,
    new_email VARCHAR(255) DEFAULT NULL
)
RETURNS profiles AS $$
DECLARE
    updated_profile profiles;
BEGIN
    UPDATE profiles 
    SET 
        first_name = COALESCE(new_first_name, first_name),
        last_name = COALESCE(new_last_name, last_name),
        email = COALESCE(new_email, email),
        updated_at = NOW()
    WHERE user_id = profile_user_id
    RETURNING * INTO updated_profile;
    
    RETURN updated_profile;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION update_user_profile(UUID, VARCHAR(100), VARCHAR(100), VARCHAR(255)) TO anon, authenticated;

-- Create a function to check if phone number exists
CREATE OR REPLACE FUNCTION phone_exists(phone_number TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS(SELECT 1 FROM profiles WHERE phone = phone_number);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION phone_exists(TEXT) TO anon, authenticated;

-- Comments for documentation
COMMENT ON TABLE profiles IS 'User profiles table storing additional user information beyond auth.users';
COMMENT ON COLUMN profiles.user_id IS 'Foreign key reference to auth.users.id';
COMMENT ON COLUMN profiles.phone IS 'User phone number in international format (e.g., +254700000000)';
COMMENT ON COLUMN profiles.role IS 'User role: admin, manager, or passenger';
COMMENT ON COLUMN profiles.is_active IS 'Whether the user account is active';

-- Success message
SELECT 'Supabase schema setup completed successfully!' as message;
