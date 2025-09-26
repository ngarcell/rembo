# Epic 4: Payment Processing & Financial Management

**Epic Goal**: Implement secure, reliable M-Pesa payment integration and comprehensive financial management for the matatu fleet system

## Overview
This epic implements the complete payment processing system that enables passengers to pay for bookings via M-Pesa, managers to track revenue and financial performance, and admins to manage financial operations. It includes M-Pesa Daraja API integration, payment receipts, refund processing, and comprehensive financial reporting.

## User Stories

### US4.1: M-Pesa STK Push Payment Integration
**As a passenger, I want to pay for bookings via M-Pesa STK Push so that I can complete transactions easily and securely**

**Acceptance Criteria:**
- Passenger can initiate M-Pesa payment directly from booking confirmation
- System sends STK Push to passenger's phone for payment authorization
- Payment status is tracked in real-time with callback handling
- Booking is automatically confirmed upon successful payment
- Failed payments are handled gracefully with retry options

**Technical Requirements:**
- Integrate M-Pesa Daraja API with STK Push functionality
- Implement secure webhook handling for payment callbacks
- Create payment status tracking and monitoring
- Add payment timeout handling and retry mechanisms
- Implement secure credential management for M-Pesa API

### US4.2: Payment Receipt Generation & Management
**As a passenger, I want to receive digital payment receipts so that I have proof of payment and transaction records**

**Acceptance Criteria:**
- Digital receipt generated immediately upon successful payment
- Receipt includes all transaction details (amount, date, booking info, M-Pesa reference)
- Receipt accessible in passenger dashboard and booking history
- Receipt can be downloaded as PDF or shared via SMS/email
- Receipt includes QR code for verification purposes

**Technical Requirements:**
- Implement PDF receipt generation system
- Create receipt template with branding and required details
- Add QR code generation for receipt verification
- Implement receipt storage and retrieval system
- Add email/SMS receipt delivery functionality

### US4.3: Payment Status Tracking & Monitoring
**As a manager, I want to track payment status and revenue so that I can manage financial operations effectively**

**Acceptance Criteria:**
- Manager can view real-time payment status for all bookings
- Payment dashboard shows daily, weekly, monthly revenue summaries
- Failed payment notifications and alerts system
- Payment reconciliation reports with M-Pesa transaction matching
- Revenue analytics by route, vehicle, and time period

**Technical Requirements:**
- Create payment monitoring dashboard
- Implement real-time payment status updates
- Add revenue analytics and reporting system
- Create payment reconciliation tools
- Implement payment alert and notification system

### US4.4: Refund Processing & Management
**As a manager, I want to process refunds for cancelled trips so that I can maintain customer satisfaction and handle cancellations properly**

**Acceptance Criteria:**
- Manager can initiate refunds for cancelled bookings
- Automated refund processing for system-cancelled trips
- Refund status tracking and confirmation
- Refund receipts generated for passengers
- Refund reconciliation with original payment records

**Technical Requirements:**
- Implement M-Pesa B2C API for refund processing
- Create refund workflow and approval system
- Add refund status tracking and notifications
- Implement refund receipt generation
- Create refund reconciliation and audit trails

### US4.5: Financial Reporting & Analytics
**As an admin, I want comprehensive financial reports so that I can analyze business performance and make strategic decisions**

**Acceptance Criteria:**
- Daily, weekly, monthly financial summary reports
- Revenue breakdown by fleet, route, vehicle, and driver
- Payment method analysis and success rates
- Refund and cancellation impact analysis
- Profit and loss statements with operational costs

**Technical Requirements:**
- Create comprehensive financial reporting system
- Implement advanced analytics and data visualization
- Add export functionality for financial reports
- Create automated report generation and scheduling
- Implement financial KPI tracking and alerts

## Definition of Done
- [ ] M-Pesa STK Push integration working end-to-end
- [ ] Payment receipt generation and delivery functional
- [ ] Payment status tracking and monitoring operational
- [ ] Refund processing system implemented
- [ ] Financial reporting and analytics complete
- [ ] All payment workflows tested with real M-Pesa sandbox
- [ ] Security audit completed for payment handling
- [ ] Performance testing passed for payment processing
- [ ] Documentation complete for all payment APIs
- [ ] Integration tests passing for all payment scenarios

## Dependencies
- Epic 3: Booking & Trip Management (for booking integration)
- M-Pesa Daraja API credentials and sandbox access
- PDF generation library for receipts
- Email/SMS service for receipt delivery
- Database schema for payment and financial data

## Technical Architecture

### Payment Processing Flow
```
1. Passenger confirms booking
2. System initiates M-Pesa STK Push
3. Passenger authorizes payment on phone
4. M-Pesa sends callback to webhook
5. System updates payment status
6. Booking confirmed and receipt generated
7. Receipt delivered to passenger
```

### Database Schema
```sql
-- Enhanced payment tracking
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY,
    booking_id UUID REFERENCES bookings(id),
    mpesa_checkout_request_id VARCHAR(100),
    mpesa_transaction_id VARCHAR(100),
    phone_number VARCHAR(15),
    amount DECIMAL(10,2),
    status payment_status,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Receipt management
CREATE TABLE payment_receipts (
    id UUID PRIMARY KEY,
    payment_id UUID REFERENCES payment_transactions(id),
    receipt_number VARCHAR(50) UNIQUE,
    pdf_path TEXT,
    qr_code TEXT,
    sent_via_email BOOLEAN DEFAULT FALSE,
    sent_via_sms BOOLEAN DEFAULT FALSE
);

-- Refund tracking
CREATE TABLE refund_transactions (
    id UUID PRIMARY KEY,
    original_payment_id UUID REFERENCES payment_transactions(id),
    mpesa_transaction_id VARCHAR(100),
    amount DECIMAL(10,2),
    reason TEXT,
    status refund_status,
    processed_by UUID REFERENCES user_profiles(id),
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Risks & Mitigation
- **Risk**: M-Pesa API downtime or failures
  - **Mitigation**: Implement retry mechanisms and fallback payment methods
- **Risk**: Payment callback security vulnerabilities
  - **Mitigation**: Implement proper webhook validation and encryption
- **Risk**: Financial data accuracy and reconciliation issues
  - **Mitigation**: Implement comprehensive audit trails and reconciliation tools
- **Risk**: Refund processing delays or failures
  - **Mitigation**: Automated refund processing with manual override capabilities

## Estimated Effort
**Story Points**: 25
**Duration**: 3-4 sprints
**Priority**: P1 (High - Critical for revenue generation)

---

**Story Owner**: Product Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Finance Team, Operations Team, Customer Support
