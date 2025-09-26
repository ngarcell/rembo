# Story 3.1: Trip Creation & Scheduling

**Epic**: Epic 3 - Booking & Trip Management  
**Story ID**: 3.1  
**Priority**: P0 (Critical)  
**Estimated Effort**: 8 Story Points  
**Status**: ✅ COMPLETED

## 📋 Story Description

**As a manager, I want to create and schedule trips so that passengers can book transportation services and I can manage fleet operations efficiently.**

## 🎯 Acceptance Criteria

### ✅ **Trip Creation**
- [x] Manager can create trips with complete details (route, schedule, pricing)
- [x] System validates vehicle and driver availability for trip times
- [x] Trip capacity automatically set based on assigned vehicle
- [x] Manager can set custom pricing per trip
- [x] System prevents scheduling conflicts for vehicles and drivers

### ✅ **Trip Scheduling**
- [x] Manager can schedule trips for future dates
- [x] Recurring trip templates for regular routes
- [x] Bulk trip creation for multiple dates
- [x] Schedule validation prevents overlapping assignments
- [x] Trip status tracking (scheduled, active, completed, cancelled)

### ✅ **Trip Management**
- [x] Manager can modify trip details before departure
- [x] Trip cancellation with passenger notifications
- [x] Real-time trip status updates
- [x] Trip history and audit trail
- [x] Integration with vehicle-driver assignments

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Trip status enum
CREATE TYPE trip_status AS ENUM (
    'scheduled', 'active', 'in_progress', 'completed', 'cancelled', 'delayed'
);

-- Routes table
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    distance_km DECIMAL(8,2),
    estimated_duration_minutes INTEGER,
    base_fare DECIMAL(10,2) NOT NULL,
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trips table
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES routes(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    driver_id UUID NOT NULL REFERENCES driver_profiles(id),
    assignment_id UUID REFERENCES vehicle_assignments(id),
    
    -- Schedule information
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP,
    actual_departure TIMESTAMP,
    actual_arrival TIMESTAMP,
    
    -- Trip details
    fare DECIMAL(10,2) NOT NULL,
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    status trip_status DEFAULT 'scheduled',
    
    -- Management
    created_by UUID NOT NULL REFERENCES user_profiles(id),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    notes TEXT,
    cancellation_reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_trip_times CHECK (
        scheduled_arrival IS NULL OR scheduled_arrival > scheduled_departure
    ),
    CONSTRAINT valid_actual_times CHECK (
        actual_arrival IS NULL OR actual_departure IS NULL OR actual_arrival >= actual_departure
    ),
    CONSTRAINT valid_seat_count CHECK (available_seats <= total_seats AND available_seats >= 0)
);

-- Trip templates for recurring trips
CREATE TABLE trip_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    route_id UUID NOT NULL REFERENCES routes(id),
    departure_time TIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    days_of_week INTEGER[] NOT NULL, -- [1,2,3,4,5] for weekdays
    is_active BOOLEAN DEFAULT true,
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    created_by UUID NOT NULL REFERENCES user_profiles(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_trips_route_date ON trips(route_id, scheduled_departure);
CREATE INDEX idx_trips_vehicle_date ON trips(vehicle_id, scheduled_departure);
CREATE INDEX idx_trips_driver_date ON trips(driver_id, scheduled_departure);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_fleet_date ON trips(fleet_id, scheduled_departure);
```

### **API Endpoints**
- `POST /api/v1/manager/trips` - Create new trip
- `GET /api/v1/manager/trips` - List trips with filtering
- `GET /api/v1/manager/trips/{id}` - Get trip details
- `PUT /api/v1/manager/trips/{id}` - Update trip details
- `DELETE /api/v1/manager/trips/{id}` - Cancel trip
- `POST /api/v1/manager/trips/bulk` - Create multiple trips
- `GET /api/v1/manager/routes` - List available routes
- `POST /api/v1/manager/routes` - Create new route
- `GET /api/v1/manager/trips/availability` - Check vehicle/driver availability

### **Pydantic Models**
```python
class RouteCreate(BaseModel):
    name: str = Field(..., max_length=255)
    origin: str = Field(..., max_length=255)
    destination: str = Field(..., max_length=255)
    distance_km: Optional[Decimal] = Field(None, ge=0)
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    base_fare: Decimal = Field(..., ge=0)

class TripCreate(BaseModel):
    route_id: str
    vehicle_id: str
    driver_id: str
    scheduled_departure: datetime
    scheduled_arrival: Optional[datetime] = None
    fare: Decimal = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class TripResponse(BaseModel):
    id: str
    route_name: str
    vehicle_info: str  # "KCS-001 (KCA123A)"
    driver_name: str
    scheduled_departure: str
    scheduled_arrival: Optional[str]
    fare: Decimal
    total_seats: int
    available_seats: int
    status: str
    created_at: str

class BulkTripCreate(BaseModel):
    template_id: str
    start_date: date
    end_date: date
    vehicle_assignments: List[Dict[str, str]]  # [{"vehicle_id": "...", "driver_id": "..."}]
```

## 🧪 Testing Strategy

### **Unit Tests**
- Trip creation validation
- Schedule conflict detection
- Seat capacity management
- Status transition logic
- Route management functions

### **Integration Tests**
- End-to-end trip creation workflow
- Vehicle-driver availability checking
- Bulk trip creation process
- Trip modification and cancellation
- Integration with assignment system

### **Edge Cases**
- Overlapping trip schedules
- Invalid vehicle-driver combinations
- Past date trip creation
- Capacity overflow scenarios
- Concurrent trip modifications

## 📊 Definition of Done

- [x] Trip creation system implemented
- [x] Route management functional
- [x] Schedule validation working
- [x] Bulk trip creation operational
- [x] Trip status management complete
- [x] All API endpoints tested
- [x] Database constraints enforced
- [ ] Frontend interface updated
- [x] Performance testing passed
- [x] Documentation complete

## 🔗 Dependencies

- **Prerequisite**: Story 2.1 (Vehicle Registration) ✅ COMPLETED
- **Prerequisite**: Story 2.2 (Driver-Vehicle Assignment)
- **Database**: PostgreSQL with advanced features
- **Authentication**: Manager role validation

## 🎯 Business Value

- **Service Delivery**: Enable core transportation service
- **Operational Control**: Manage fleet schedules efficiently
- **Revenue Generation**: Create bookable trips for passengers
- **Resource Optimization**: Prevent scheduling conflicts
- **Scalability**: Support growing fleet operations

## 📝 Implementation Notes

- Implement atomic operations for trip creation
- Use database constraints for data integrity
- Consider time zone handling for scheduling
- Implement soft deletes for audit trail
- Add validation for business rules
- Consider caching for route data

---

**Story Owner**: Operations Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Fleet Managers, Drivers, Operations Team
