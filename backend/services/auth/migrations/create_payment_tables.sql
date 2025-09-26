-- Migration: Create payment processing tables for M-Pesa integration
-- Date: 2024-09-26
-- Description: Creates tables for payment transactions, receipts, refunds, and webhook logs

-- Create payment status enum
CREATE TYPE payment_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'expired',
    'refunded'
);

-- Create refund status enum
CREATE TYPE refund_status AS ENUM (
    'pending',
    'approved',
    'processing',
    'completed',
    'failed',
    'cancelled'
);

-- Create refund reason enum
CREATE TYPE refund_reason AS ENUM (
    'trip_cancelled_by_operator',
    'vehicle_breakdown',
    'weather_conditions',
    'passenger_request',
    'duplicate_booking',
    'system_error',
    'other'
);

-- Payment transactions table
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    -- M-Pesa specific fields
    checkout_request_id VARCHAR(100) UNIQUE,
    merchant_request_id VARCHAR(100),
    phone_number VARCHAR(15) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    
    -- Transaction tracking
    mpesa_receipt_number VARCHAR(100) UNIQUE,
    transaction_date TIMESTAMP WITH TIME ZONE,
    status payment_status DEFAULT 'pending' NOT NULL,
    
    -- Payment metadata
    account_reference VARCHAR(50),
    transaction_desc TEXT,
    payment_reference VARCHAR(50) UNIQUE NOT NULL,
    
    -- Gateway response data
    gateway_response TEXT,
    failure_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT payment_transactions_positive_amount CHECK (amount > 0)
);

-- Create indexes for payment_transactions
CREATE INDEX idx_payment_transactions_booking_id ON payment_transactions(booking_id);
CREATE INDEX idx_payment_transactions_checkout_request_id ON payment_transactions(checkout_request_id);
CREATE INDEX idx_payment_transactions_payment_reference ON payment_transactions(payment_reference);
CREATE INDEX idx_payment_transactions_status_created ON payment_transactions(status, created_at);
CREATE INDEX idx_payment_transactions_phone_created ON payment_transactions(phone_number, created_at);
CREATE INDEX idx_payment_transactions_mpesa_receipt ON payment_transactions(mpesa_receipt_number);

-- Payment receipts table
CREATE TABLE payment_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES payment_transactions(id) ON DELETE CASCADE,
    
    -- Receipt identification
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_type VARCHAR(20) DEFAULT 'PAYMENT' NOT NULL,
    
    -- File management
    pdf_file_path TEXT,
    pdf_file_size INTEGER,
    qr_code_data TEXT,
    
    -- Delivery tracking
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP WITH TIME ZONE,
    sms_sent BOOLEAN DEFAULT FALSE,
    sms_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Verification
    verification_hash VARCHAR(256),
    verification_count INTEGER DEFAULT 0,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for payment_receipts
CREATE INDEX idx_payment_receipts_payment_id ON payment_receipts(payment_id);
CREATE INDEX idx_payment_receipts_receipt_number ON payment_receipts(receipt_number);
CREATE INDEX idx_payment_receipts_created_at ON payment_receipts(created_at);

-- Refund transactions table
CREATE TABLE refund_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_payment_id UUID NOT NULL REFERENCES payment_transactions(id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    -- Refund details
    refund_amount DECIMAL(10,2) NOT NULL CHECK (refund_amount > 0),
    refund_reason refund_reason NOT NULL,
    refund_notes TEXT,
    
    -- M-Pesa B2C details
    mpesa_transaction_id VARCHAR(100),
    mpesa_conversation_id VARCHAR(100),
    mpesa_originator_conversation_id VARCHAR(100),
    
    -- Approval workflow
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES user_profiles(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Status tracking
    status refund_status DEFAULT 'pending' NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing metadata
    processed_by UUID REFERENCES user_profiles(id),
    processing_method VARCHAR(20) DEFAULT 'MPESA_B2C' NOT NULL,
    
    -- Gateway response
    gateway_response TEXT,
    failure_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT refund_transactions_positive_amount CHECK (refund_amount > 0)
);

-- Create indexes for refund_transactions
CREATE INDEX idx_refund_transactions_original_payment_id ON refund_transactions(original_payment_id);
CREATE INDEX idx_refund_transactions_booking_id ON refund_transactions(booking_id);
CREATE INDEX idx_refund_transactions_status_created ON refund_transactions(status, created_at);
CREATE INDEX idx_refund_transactions_approved_by ON refund_transactions(approved_by);
CREATE INDEX idx_refund_transactions_processed_by ON refund_transactions(processed_by);

-- Payment webhook logs table
CREATE TABLE payment_webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Webhook details
    checkout_request_id VARCHAR(100),
    webhook_type VARCHAR(50) NOT NULL,
    
    -- Request data
    raw_payload TEXT NOT NULL,
    headers TEXT,
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for payment_webhook_logs
CREATE INDEX idx_payment_webhook_logs_checkout_request_id ON payment_webhook_logs(checkout_request_id);
CREATE INDEX idx_payment_webhook_logs_processed ON payment_webhook_logs(processed, received_at);
CREATE INDEX idx_payment_webhook_logs_webhook_type ON payment_webhook_logs(webhook_type);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_payment_transactions_updated_at 
    BEFORE UPDATE ON payment_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_receipts_updated_at 
    BEFORE UPDATE ON payment_receipts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_refund_transactions_updated_at 
    BEFORE UPDATE ON refund_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add relationship to bookings table for payment transactions
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_transaction_id UUID REFERENCES payment_transactions(id);
CREATE INDEX IF NOT EXISTS idx_bookings_payment_transaction_id ON bookings(payment_transaction_id);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON payment_transactions TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON payment_receipts TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON refund_transactions TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON payment_webhook_logs TO postgres;

-- Insert sample data for testing (sandbox environment only)
-- This should be removed in production
INSERT INTO payment_transactions (
    booking_id,
    phone_number,
    amount,
    payment_reference,
    account_reference,
    transaction_desc,
    status
) VALUES (
    (SELECT id FROM bookings LIMIT 1),
    '254708374149',
    500.00,
    'PAY-TEST001',
    'PAY-TEST001',
    'Test payment transaction',
    'completed'
) ON CONFLICT DO NOTHING;

COMMIT;
