# Story 3.3: Real-time Trip Status Updates

**Epic**: Epic 3 - Booking & Trip Management  
**Story ID**: 3.3  
**Priority**: P1 (High)  
**Estimated Effort**: 7 Story Points  
**Status**: 🔄 NOT_STARTED

## 📋 Story Description

**As a passenger and manager, I want to receive real-time trip status updates so that I can track trip progress, receive timely notifications, and make informed decisions about my journey.**

## 🎯 Acceptance Criteria

### ✅ **Real-time Status Tracking**
- [ ] System tracks trip status in real-time (scheduled, departed, in-transit, arrived, completed)
- [ ] GPS integration provides live location updates
- [ ] Estimated arrival times updated based on current location and traffic
- [ ] Delay notifications sent automatically when trips are running late
- [ ] Status updates visible to both passengers and managers

### ✅ **Passenger Notifications**
- [ ] SMS notifications for trip status changes
- [ ] Email notifications for significant updates
- [ ] Push notifications for mobile app users
- [ ] Customizable notification preferences
- [ ] Emergency notifications for trip cancellations or major delays

### ✅ **Manager Dashboard**
- [ ] Real-time fleet tracking dashboard
- [ ] Trip progress monitoring for all active trips
- [ ] Alert system for delayed or problematic trips
- [ ] Driver communication interface
- [ ] Historical trip performance data

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Trip status updates table
CREATE TABLE trip_status_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    status trip_status NOT NULL,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_name VARCHAR(255),
    estimated_arrival TIMESTAMP,
    delay_minutes INTEGER DEFAULT 0,
    update_source VARCHAR(50) DEFAULT 'system', -- system, driver, gps, manual
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Index for performance
    INDEX idx_trip_status_updates_trip_time (trip_id, created_at)
);

-- Notification preferences
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    sms_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    trip_updates BOOLEAN DEFAULT true,
    delay_alerts BOOLEAN DEFAULT true,
    cancellation_alerts BOOLEAN DEFAULT true,
    promotional BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Notification queue
CREATE TABLE notification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id),
    trip_id UUID REFERENCES trips(id),
    booking_id UUID REFERENCES bookings(id),
    notification_type VARCHAR(50) NOT NULL, -- trip_update, delay_alert, cancellation, etc.
    channel VARCHAR(20) NOT NULL, -- sms, email, push
    recipient VARCHAR(255) NOT NULL, -- phone number or email
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, retry
    scheduled_at TIMESTAMP DEFAULT NOW(),
    sent_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- GPS tracking data
CREATE TABLE gps_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    trip_id UUID REFERENCES trips(id),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed_kmh DECIMAL(5, 2),
    heading DECIMAL(5, 2), -- compass direction
    accuracy_meters INTEGER,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for geospatial queries
    INDEX idx_gps_tracking_vehicle_time (vehicle_id, timestamp),
    INDEX idx_gps_tracking_trip (trip_id, timestamp)
);

-- Add real-time fields to trips table
ALTER TABLE trips ADD COLUMN current_lat DECIMAL(10, 8);
ALTER TABLE trips ADD COLUMN current_lng DECIMAL(11, 8);
ALTER TABLE trips ADD COLUMN current_location VARCHAR(255);
ALTER TABLE trips ADD COLUMN estimated_arrival TIMESTAMP;
ALTER TABLE trips ADD COLUMN delay_minutes INTEGER DEFAULT 0;
ALTER TABLE trips ADD COLUMN last_update TIMESTAMP DEFAULT NOW();
```

### **API Endpoints**
- `GET /api/v1/trips/{id}/status` - Get current trip status
- `POST /api/v1/trips/{id}/status` - Update trip status (driver/system)
- `GET /api/v1/trips/{id}/tracking` - Get GPS tracking history
- `POST /api/v1/trips/{id}/location` - Update current location
- `GET /api/v1/bookings/{id}/status` - Get booking trip status
- `GET /api/v1/manager/trips/active` - Get all active trips status
- `POST /api/v1/notifications/preferences` - Update notification preferences
- `GET /api/v1/notifications/history` - Get notification history
- `WebSocket /ws/trip/{id}` - Real-time trip updates

### **Pydantic Models**
```python
class TripStatusUpdate(BaseModel):
    status: str = Field(..., regex=r'^(scheduled|departed|in_transit|arrived|completed|cancelled|delayed)$')
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    estimated_arrival: Optional[datetime] = None
    delay_minutes: Optional[int] = Field(0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class TripStatusResponse(BaseModel):
    trip_id: str
    current_status: str
    current_location: Optional[str]
    estimated_arrival: Optional[str]
    delay_minutes: int
    last_update: str
    route_progress: Optional[Decimal]  # percentage completed
    next_stop: Optional[str]

class NotificationPreferences(BaseModel):
    sms_enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = True
    trip_updates: bool = True
    delay_alerts: bool = True
    cancellation_alerts: bool = True
    promotional: bool = False

class GPSLocation(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    speed_kmh: Optional[Decimal] = Field(None, ge=0)
    heading: Optional[Decimal] = Field(None, ge=0, lt=360)
    accuracy_meters: Optional[int] = Field(None, ge=0)
    timestamp: datetime
```

## 🧪 Testing Strategy

### **Unit Tests**
- Status update validation
- Notification triggering logic
- GPS data processing
- Delay calculation algorithms
- WebSocket connection handling

### **Integration Tests**
- End-to-end status update flow
- Notification delivery system
- GPS integration testing
- Real-time dashboard updates
- WebSocket communication

### **Performance Tests**
- High-frequency GPS updates
- Concurrent status updates
- Notification queue processing
- WebSocket scalability
- Database query performance

## 📊 Definition of Done

- [ ] Real-time status tracking implemented
- [ ] GPS integration functional
- [ ] Notification system operational
- [ ] WebSocket real-time updates working
- [ ] Manager dashboard complete
- [ ] Passenger status interface ready
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] API documentation complete
- [ ] Mobile app integration ready

## 🔗 Dependencies

- **Prerequisite**: Story 3.1 (Trip Creation & Scheduling)
- **Prerequisite**: Story 3.2 (Passenger Seat Booking)
- **GPS Provider**: For location tracking
- **SMS Gateway**: For SMS notifications
- **Email Service**: For email notifications
- **WebSocket Support**: For real-time updates
- **Push Notification Service**: For mobile notifications

## 🎯 Business Value

- **Customer Experience**: Keep passengers informed
- **Operational Efficiency**: Real-time fleet monitoring
- **Trust Building**: Transparent trip progress
- **Problem Resolution**: Early detection of issues
- **Competitive Advantage**: Superior service quality

## 📝 Implementation Notes

- Implement WebSocket for real-time updates
- Use background tasks for notification processing
- Consider GPS data privacy and security
- Implement efficient geospatial queries
- Add rate limiting for location updates
- Use message queues for notification reliability

---

**Story Owner**: Product Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Passengers, Drivers, Fleet Managers, Customer Service
