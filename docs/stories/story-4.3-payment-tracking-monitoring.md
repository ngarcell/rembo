# Story 4.3: Payment Status Tracking & Monitoring

**Epic**: Epic 4 - Payment Processing & Financial Management  
**Story ID**: US4.3  
**Priority**: P1 (High)  
**Story Points**: 6  
**Status**: 🔄 NOT_STARTED

## Story Description
**As a manager, I want to track payment status and revenue so that I can manage financial operations effectively**

## Acceptance Criteria

### AC4.3.1: Real-time Payment Dashboard
- [ ] Manager can view real-time payment status for all bookings in their fleet
- [ ] Dashboard shows pending, completed, failed, and refunded payments
- [ ] Payment status updates automatically without page refresh
- [ ] Filter payments by date range, status, route, and vehicle
- [ ] Search payments by passenger name, phone number, or transaction ID

### AC4.3.2: Revenue Analytics & Reporting
- [ ] Daily, weekly, monthly revenue summaries displayed
- [ ] Revenue breakdown by route, vehicle, and driver
- [ ] Payment method analysis (M-Pesa vs other methods)
- [ ] Revenue trends and growth analytics
- [ ] Comparison with previous periods (day-over-day, month-over-month)

### AC4.3.3: Payment Monitoring & Alerts
- [ ] Failed payment notifications sent to managers
- [ ] High-value transaction alerts for security monitoring
- [ ] Payment reconciliation discrepancy alerts
- [ ] Daily revenue summary notifications
- [ ] Unusual payment pattern detection and alerts

### AC4.3.4: Financial Reconciliation Tools
- [ ] Payment reconciliation with M-Pesa transaction records
- [ ] Automated matching of payments with M-Pesa statements
- [ ] Discrepancy identification and reporting
- [ ] Manual reconciliation tools for unmatched transactions
- [ ] Reconciliation audit trail and reporting

## Technical Requirements

### TR4.3.1: Payment Monitoring Dashboard
- [ ] Create real-time payment dashboard with WebSocket updates
- [ ] Implement payment filtering and search functionality
- [ ] Add payment status visualization and charts
- [ ] Create responsive dashboard for mobile and desktop
- [ ] Implement dashboard data caching for performance

### TR4.3.2: Revenue Analytics Engine
- [ ] Implement revenue calculation and aggregation services
- [ ] Create analytics data models and views
- [ ] Add revenue trend analysis algorithms
- [ ] Implement comparative analytics (period-over-period)
- [ ] Create revenue forecasting capabilities

### TR4.3.3: Alert & Notification System
- [ ] Implement payment alert engine with configurable rules
- [ ] Create notification delivery system (email, SMS, in-app)
- [ ] Add alert escalation and acknowledgment features
- [ ] Implement alert history and audit logging
- [ ] Create alert management interface for managers

### TR4.3.4: Reconciliation & Audit System
- [ ] Implement automated reconciliation engine
- [ ] Create M-Pesa statement import and parsing
- [ ] Add transaction matching algorithms
- [ ] Implement discrepancy detection and reporting
- [ ] Create audit trail for all financial operations

## Implementation Details

### Database Schema
```sql
-- Payment monitoring views
CREATE VIEW payment_summary AS
SELECT 
    DATE(created_at) as payment_date,
    status,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    fleet_id
FROM payment_transactions pt
JOIN bookings b ON pt.booking_id = b.id
GROUP BY DATE(created_at), status, fleet_id;

-- Revenue analytics table
CREATE TABLE revenue_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    
    -- Time period
    period_type period_type NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Revenue metrics
    total_revenue DECIMAL(12,2) NOT NULL,
    transaction_count INTEGER NOT NULL,
    average_transaction DECIMAL(10,2),
    
    -- Breakdown
    revenue_by_route JSONB,
    revenue_by_vehicle JSONB,
    revenue_by_payment_method JSONB,
    
    -- Timestamps
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(fleet_id, period_type, period_start)
);

-- Alert configuration
CREATE TABLE payment_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    
    -- Alert configuration
    alert_type alert_type NOT NULL,
    alert_name VARCHAR(100) NOT NULL,
    conditions JSONB NOT NULL,
    
    -- Notification settings
    notification_methods TEXT[] DEFAULT ARRAY['email'],
    recipients UUID[] NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reconciliation records
CREATE TABLE payment_reconciliation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Reconciliation period
    reconciliation_date DATE NOT NULL,
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    
    -- Reconciliation results
    system_total DECIMAL(12,2) NOT NULL,
    mpesa_total DECIMAL(12,2) NOT NULL,
    difference DECIMAL(12,2) NOT NULL,
    
    -- Status
    status reconciliation_status DEFAULT 'PENDING',
    reconciled_by UUID REFERENCES user_profiles(id),
    reconciled_at TIMESTAMP,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints
```python
# Payment dashboard data
GET /api/v1/payments/dashboard
?fleet_id=uuid&date_from=2024-01-01&date_to=2024-01-31

# Revenue analytics
GET /api/v1/analytics/revenue
?fleet_id=uuid&period=monthly&year=2024

# Payment alerts
GET /api/v1/payments/alerts
POST /api/v1/payments/alerts
PUT /api/v1/payments/alerts/{alert_id}

# Reconciliation
POST /api/v1/payments/reconcile
GET /api/v1/payments/reconciliation/{date}
```

### Service Implementation
```python
class PaymentMonitoringService:
    async def get_dashboard_data(self, fleet_id: UUID, filters: dict):
        # Fetch payment statistics
        # Calculate revenue metrics
        # Get payment status breakdown
        # Return dashboard data
        
    async def calculate_revenue_analytics(self, fleet_id: UUID, period: str):
        # Aggregate revenue data
        # Calculate trends and comparisons
        # Generate analytics insights
        # Cache results for performance
        
class PaymentAlertService:
    async def check_alert_conditions(self):
        # Evaluate all active alerts
        # Identify triggered conditions
        # Send notifications
        # Log alert activities
        
class ReconciliationService:
    async def reconcile_payments(self, date: datetime, fleet_id: UUID):
        # Fetch system payment records
        # Import M-Pesa statement data
        # Match transactions
        # Identify discrepancies
        # Generate reconciliation report
```

## Testing Requirements

### Unit Tests
- [ ] Dashboard data aggregation tests
- [ ] Revenue calculation tests
- [ ] Alert condition evaluation tests
- [ ] Reconciliation logic tests
- [ ] Analytics computation tests

### Integration Tests
- [ ] Dashboard API integration tests
- [ ] Real-time update tests
- [ ] Alert notification tests
- [ ] M-Pesa reconciliation tests
- [ ] Analytics data accuracy tests

### Performance Tests
- [ ] Dashboard loading performance tests
- [ ] Large dataset analytics tests
- [ ] Real-time update performance tests
- [ ] Concurrent user dashboard tests
- [ ] Alert processing performance tests

## Definition of Done
- [ ] Payment monitoring dashboard implemented and functional
- [ ] Revenue analytics and reporting operational
- [ ] Alert system configured and tested
- [ ] Reconciliation tools working accurately
- [ ] Real-time updates functioning properly
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests with payment system passing
- [ ] Performance tests meeting requirements
- [ ] Documentation complete for monitoring system
- [ ] Code review completed and approved
- [ ] User acceptance testing completed
- [ ] Ready for production deployment

## Dependencies
- Payment processing system (Story 4.1) for payment data
- User authentication system for manager access control
- Real-time communication system (WebSocket/SSE)
- M-Pesa statement import capabilities
- Email/SMS notification services
- Analytics and reporting infrastructure

## Risks & Mitigation
- **Risk**: Dashboard performance with large datasets
  - **Mitigation**: Implement data pagination, caching, and aggregation
- **Risk**: Real-time update scalability issues
  - **Mitigation**: Use efficient WebSocket management and data streaming
- **Risk**: Reconciliation accuracy problems
  - **Mitigation**: Implement comprehensive testing and manual override capabilities

---

**Assigned To**: Backend Development Team, Frontend Team  
**Reviewer**: Technical Lead, Finance Team  
**Estimated Hours**: 35-40 hours  
**Sprint**: TBD
