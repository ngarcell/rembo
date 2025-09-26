# Story 4.2: Payment Receipt Generation & Management

**Epic**: Epic 4 - Payment Processing & Financial Management  
**Story ID**: US4.2  
**Priority**: P1 (High)  
**Story Points**: 5  
**Status**: 🔄 NOT_STARTED

## Story Description
**As a passenger, I want to receive digital payment receipts so that I have proof of payment and transaction records**

## Acceptance Criteria

### AC4.2.1: Automatic Receipt Generation
- [ ] Digital receipt generated immediately upon successful payment
- [ ] Receipt includes all required transaction details (amount, date, booking info, M-Pesa reference)
- [ ] Receipt formatted professionally with company branding
- [ ] Unique receipt number generated for each transaction
- [ ] Receipt generation completes within 10 seconds of payment confirmation

### AC4.2.2: Receipt Content & Format
- [ ] Receipt includes passenger details (name, phone number)
- [ ] Trip details displayed (route, date, time, seat numbers)
- [ ] Payment information shown (amount, M-Pesa transaction ID, payment date)
- [ ] QR code included for receipt verification
- [ ] Company logo and contact information displayed
- [ ] Receipt available in PDF format for download

### AC4.2.3: Receipt Access & Delivery
- [ ] Receipt accessible in passenger dashboard immediately
- [ ] Receipt viewable in booking history section
- [ ] Receipt downloadable as PDF file
- [ ] Receipt shareable via email or SMS
- [ ] Receipt accessible offline once downloaded

### AC4.2.4: Receipt Verification & Security
- [ ] QR code enables receipt verification by scanning
- [ ] Receipt tampering detection mechanisms in place
- [ ] Digital signature or watermark for authenticity
- [ ] Receipt verification API for third-party validation
- [ ] Secure storage of receipt data and files

## Technical Requirements

### TR4.2.1: PDF Generation System
- [ ] Implement PDF generation library (ReportLab or WeasyPrint)
- [ ] Create professional receipt template with branding
- [ ] Add dynamic content rendering for transaction details
- [ ] Implement QR code generation and embedding
- [ ] Optimize PDF generation for performance and file size

### TR4.2.2: Receipt Storage & Management
- [ ] Create receipt storage system (local/cloud storage)
- [ ] Implement receipt file naming and organization
- [ ] Add receipt metadata tracking in database
- [ ] Create receipt retrieval and serving endpoints
- [ ] Implement receipt cleanup and archival policies

### TR4.2.3: Delivery & Notification System
- [ ] Integrate email service for receipt delivery
- [ ] Implement SMS service for receipt links
- [ ] Create receipt notification templates
- [ ] Add delivery status tracking and retry mechanisms
- [ ] Implement delivery preference management

### TR4.2.4: Verification & Security
- [ ] Implement QR code generation with receipt data
- [ ] Create receipt verification API endpoint
- [ ] Add digital signature or hash for receipt integrity
- [ ] Implement secure receipt access controls
- [ ] Add audit logging for receipt access and modifications

## Implementation Details

### Database Schema
```sql
-- Receipt management table
CREATE TABLE payment_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES payment_transactions(id),
    
    -- Receipt identification
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_type receipt_type DEFAULT 'PAYMENT',
    
    -- File management
    pdf_file_path TEXT,
    pdf_file_size INTEGER,
    qr_code_data TEXT,
    
    -- Delivery tracking
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,
    sms_sent BOOLEAN DEFAULT FALSE,
    sms_sent_at TIMESTAMP,
    
    -- Verification
    verification_hash VARCHAR(256),
    verification_count INTEGER DEFAULT 0,
    last_verified_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Receipt type enum
CREATE TYPE receipt_type AS ENUM (
    'PAYMENT',
    'REFUND',
    'CANCELLATION'
);
```

### API Endpoints
```python
# Generate receipt
POST /api/v1/receipts/generate
{
    "payment_id": "uuid",
    "delivery_method": ["email", "sms"]
}

# Get receipt
GET /api/v1/receipts/{receipt_id}

# Download receipt PDF
GET /api/v1/receipts/{receipt_id}/download

# Verify receipt
POST /api/v1/receipts/verify
{
    "qr_code_data": "encrypted_receipt_data"
}

# Resend receipt
POST /api/v1/receipts/{receipt_id}/resend
```

### Service Implementation
```python
class ReceiptService:
    async def generate_receipt(self, payment_id: UUID, delivery_methods: List[str]):
        # Fetch payment and booking details
        # Generate unique receipt number
        # Create PDF with template
        # Generate QR code
        # Store receipt record
        # Trigger delivery
        
    async def deliver_receipt(self, receipt_id: UUID, methods: List[str]):
        # Send via email if requested
        # Send via SMS if requested
        # Update delivery status
        # Handle delivery failures
        
    async def verify_receipt(self, qr_data: str) -> dict:
        # Decode QR data
        # Verify receipt authenticity
        # Return verification result
```

## Testing Requirements

### Unit Tests
- [ ] PDF generation tests
- [ ] QR code generation tests
- [ ] Receipt template rendering tests
- [ ] Delivery service tests
- [ ] Verification logic tests

### Integration Tests
- [ ] End-to-end receipt generation tests
- [ ] Email delivery integration tests
- [ ] SMS delivery integration tests
- [ ] File storage integration tests
- [ ] Receipt verification tests

### Performance Tests
- [ ] PDF generation performance tests
- [ ] Concurrent receipt generation tests
- [ ] File storage performance tests
- [ ] Delivery service performance tests
- [ ] Receipt retrieval performance tests

## Definition of Done
- [ ] Receipt generation system implemented and tested
- [ ] PDF templates created with professional design
- [ ] QR code generation and verification working
- [ ] Email and SMS delivery functional
- [ ] Receipt storage and retrieval operational
- [ ] Verification API implemented and tested
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests with email/SMS services passing
- [ ] Performance tests meeting requirements
- [ ] Documentation complete for receipt system
- [ ] Code review completed and approved
- [ ] Security review for receipt handling completed
- [ ] Ready for production deployment

## Dependencies
- Payment processing system (Story 4.1) for payment data
- Email service integration (SendGrid, AWS SES, or similar)
- SMS service integration (Africa's Talking or similar)
- PDF generation library and templates
- File storage system (local or cloud storage)
- QR code generation library

## Risks & Mitigation
- **Risk**: PDF generation performance issues
  - **Mitigation**: Implement async processing and caching
- **Risk**: Email/SMS delivery failures
  - **Mitigation**: Implement retry mechanisms and alternative delivery methods
- **Risk**: Receipt storage scalability
  - **Mitigation**: Implement cloud storage and archival policies

---

**Assigned To**: Backend Development Team  
**Reviewer**: Technical Lead, UX Team  
**Estimated Hours**: 25-30 hours  
**Sprint**: TBD
