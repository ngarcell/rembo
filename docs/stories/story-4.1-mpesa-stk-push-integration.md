# Story 4.1: M-Pesa STK Push Payment Integration

**Epic**: Epic 4 - Payment Processing & Financial Management  
**Story ID**: US4.1  
**Priority**: P1 (High)  
**Story Points**: 8  
**Status**: 🔄 NOT_STARTED

## Story Description
**As a passenger, I want to pay for bookings via M-Pesa STK Push so that I can complete transactions easily and securely**

## Acceptance Criteria

### AC4.1.1: STK Push Initiation
- [ ] Passenger can initiate M-Pesa payment directly from booking confirmation screen
- [ ] System validates phone number format and M-Pesa eligibility
- [ ] STK Push request sent to passenger's phone within 5 seconds
- [ ] Payment amount and booking details clearly displayed in STK prompt
- [ ] System generates unique payment reference for tracking

### AC4.1.2: Real-time Payment Processing
- [ ] System tracks payment status in real-time via M-Pesa callbacks
- [ ] Payment timeout handled gracefully (120 seconds default)
- [ ] Multiple payment attempts allowed for failed transactions
- [ ] Payment status updates reflected immediately in UI
- [ ] Concurrent payment requests handled properly

### AC4.1.3: Payment Confirmation & Booking Update
- [ ] Booking automatically confirmed upon successful payment
- [ ] Seat reservation converted from pending to confirmed
- [ ] Payment confirmation notification sent to passenger
- [ ] Booking status updated across all related systems
- [ ] Payment receipt generation triggered automatically

### AC4.1.4: Error Handling & Recovery
- [ ] Failed payments handled with clear error messages
- [ ] Network timeout scenarios managed gracefully
- [ ] Invalid phone number errors displayed appropriately
- [ ] Insufficient funds errors communicated clearly
- [ ] Retry mechanism available for failed payments

## Technical Requirements

### TR4.1.1: M-Pesa Daraja API Integration
- [ ] Integrate M-Pesa Daraja API v2 with STK Push endpoint
- [ ] Implement OAuth token management for API authentication
- [ ] Configure sandbox and production environment settings
- [ ] Add proper error handling for API responses
- [ ] Implement rate limiting and request throttling

### TR4.1.2: Webhook & Callback Handling
- [ ] Create secure webhook endpoint for M-Pesa callbacks
- [ ] Implement callback signature verification
- [ ] Add idempotency handling for duplicate callbacks
- [ ] Create callback processing queue for reliability
- [ ] Implement callback retry mechanism for failures

### TR4.1.3: Payment Status Management
- [ ] Create payment status tracking system
- [ ] Implement real-time status updates via WebSocket/SSE
- [ ] Add payment timeout handling and cleanup
- [ ] Create payment audit trail and logging
- [ ] Implement payment reconciliation tools

### TR4.1.4: Security & Compliance
- [ ] Encrypt sensitive payment data at rest and in transit
- [ ] Implement PCI DSS compliance measures
- [ ] Add request/response logging for audit purposes
- [ ] Implement secure credential management
- [ ] Add payment fraud detection mechanisms

## Implementation Details

### Database Schema
```sql
-- Payment transactions table
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id),
    
    -- M-Pesa specific fields
    checkout_request_id VARCHAR(100) UNIQUE,
    merchant_request_id VARCHAR(100),
    phone_number VARCHAR(15) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    
    -- Transaction tracking
    mpesa_receipt_number VARCHAR(100),
    transaction_date TIMESTAMP,
    status payment_status DEFAULT 'PENDING',
    
    -- Metadata
    account_reference VARCHAR(50),
    transaction_desc TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '2 minutes')
);

-- Payment status enum
CREATE TYPE payment_status AS ENUM (
    'PENDING',
    'PROCESSING', 
    'COMPLETED',
    'FAILED',
    'CANCELLED',
    'EXPIRED',
    'REFUNDED'
);
```

### API Endpoints
```python
# Payment initiation
POST /api/v1/payments/initiate
{
    "booking_id": "uuid",
    "phone_number": "254708374149",
    "amount": 500.00
}

# Payment status check
GET /api/v1/payments/{payment_id}/status

# M-Pesa callback webhook
POST /api/v1/payments/mpesa/callback
```

### Service Implementation
```python
class MpesaPaymentService:
    async def initiate_stk_push(self, booking_id: UUID, phone: str, amount: Decimal):
        # Generate payment reference
        # Call M-Pesa STK Push API
        # Store payment transaction
        # Return checkout request ID
        
    async def handle_callback(self, callback_data: dict):
        # Verify callback signature
        # Update payment status
        # Confirm booking if successful
        # Trigger receipt generation
```

## Testing Requirements

### Unit Tests
- [ ] M-Pesa API integration tests
- [ ] Payment status tracking tests
- [ ] Callback handling tests
- [ ] Error scenario tests
- [ ] Security validation tests

### Integration Tests
- [ ] End-to-end payment flow tests
- [ ] M-Pesa sandbox integration tests
- [ ] Webhook callback tests
- [ ] Database transaction tests
- [ ] Concurrent payment tests

### Performance Tests
- [ ] Payment processing latency tests
- [ ] Concurrent payment handling tests
- [ ] API rate limiting tests
- [ ] Database performance tests
- [ ] Memory usage optimization tests

## Definition of Done
- [ ] M-Pesa STK Push integration implemented and tested
- [ ] Payment callback handling working reliably
- [ ] Payment status tracking operational
- [ ] Error handling comprehensive and user-friendly
- [ ] Security measures implemented and audited
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests with M-Pesa sandbox passing
- [ ] Performance tests meeting requirements
- [ ] Documentation complete for API and integration
- [ ] Code review completed and approved
- [ ] Security review completed
- [ ] Ready for production deployment

## Dependencies
- M-Pesa Daraja API credentials and sandbox access
- Booking system (Story 3.2) for booking confirmation
- User authentication system for passenger verification
- Database schema for payment tracking
- Webhook infrastructure for callback handling

## Risks & Mitigation
- **Risk**: M-Pesa API rate limiting or downtime
  - **Mitigation**: Implement retry mechanisms and queue-based processing
- **Risk**: Callback delivery failures
  - **Mitigation**: Implement callback verification and manual reconciliation tools
- **Risk**: Payment security vulnerabilities
  - **Mitigation**: Security audit and penetration testing

---

**Assigned To**: Backend Development Team  
**Reviewer**: Technical Lead, Security Team  
**Estimated Hours**: 40-50 hours  
**Sprint**: TBD
