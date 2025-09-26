# Story 2.2: Driver-Vehicle Assignment

**Epic**: Epic 2 - Fleet & Vehicle Management  
**Story ID**: 2.2  
**Priority**: P0 (Critical)  
**Estimated Effort**: 5 Story Points  
**Status**: ✅ COMPLETED

## 📋 Story Description

**As a manager, I want to assign drivers to vehicles so that I can manage fleet operations efficiently and track driver-vehicle relationships for accountability and operational control.**

## 🎯 Acceptance Criteria

### ✅ **Core Functionality**
- [x] Manager can assign any driver to any vehicle in their fleet
- [x] System prevents double-assignment of vehicles (one driver per vehicle at a time)
- [x] System prevents double-assignment of drivers (one vehicle per driver at a time)
- [x] Assignment history is maintained with timestamps
- [x] Manager can reassign drivers as needed
- [x] Manager can unassign drivers from vehicles
- [x] System tracks assignment duration and changes

### ✅ **Data Validation**
- [x] Only active drivers can be assigned to vehicles
- [x] Only active vehicles can have driver assignments
- [x] Manager can only assign drivers and vehicles within their fleet
- [x] Assignment conflicts are detected and prevented
- [x] Proper error messages for invalid assignments

### ✅ **Business Logic**
- [x] Current assignments are easily identifiable
- [x] Assignment changes trigger audit log entries
- [x] Assignment status affects trip creation eligibility
- [x] Unassigned vehicles cannot be used for trips
- [x] Assignment history supports reporting and analytics

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Vehicle assignments table
CREATE TABLE vehicle_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES driver_profiles(id) ON DELETE CASCADE,
    manager_id UUID NOT NULL REFERENCES user_profiles(id),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    unassigned_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT true,
    assignment_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_active_vehicle_assignment 
        EXCLUDE (vehicle_id WITH =) WHERE (is_active = true),
    CONSTRAINT unique_active_driver_assignment 
        EXCLUDE (driver_id WITH =) WHERE (is_active = true),
    CONSTRAINT valid_assignment_period 
        CHECK (unassigned_at IS NULL OR unassigned_at > assigned_at)
);

-- Indexes for performance
CREATE INDEX idx_vehicle_assignments_vehicle_id ON vehicle_assignments(vehicle_id);
CREATE INDEX idx_vehicle_assignments_driver_id ON vehicle_assignments(driver_id);
CREATE INDEX idx_vehicle_assignments_active ON vehicle_assignments(is_active) WHERE is_active = true;
CREATE INDEX idx_vehicle_assignments_fleet_id ON vehicle_assignments(fleet_id);
```

### **API Endpoints**
- `POST /api/v1/manager/assignments` - Create driver-vehicle assignment
- `GET /api/v1/manager/assignments` - List current assignments with filtering
- `GET /api/v1/manager/assignments/history` - Get assignment history
- `PUT /api/v1/manager/assignments/{id}` - Update assignment (reassign)
- `DELETE /api/v1/manager/assignments/{id}` - Unassign driver from vehicle
- `GET /api/v1/manager/assignments/available-drivers` - Get unassigned drivers
- `GET /api/v1/manager/assignments/available-vehicles` - Get unassigned vehicles

### **Pydantic Models**
```python
class AssignmentRequest(BaseModel):
    driver_id: str = Field(..., description="Driver UUID")
    vehicle_id: str = Field(..., description="Vehicle UUID")
    assignment_notes: Optional[str] = Field(None, max_length=500)

class AssignmentResponse(BaseModel):
    id: str
    driver_id: str
    vehicle_id: str
    driver_name: str
    vehicle_info: str  # "KCS-001 (KCA123A)"
    assigned_at: str
    is_active: bool
    assignment_notes: Optional[str]

class AssignmentListResponse(BaseModel):
    assignments: List[AssignmentResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int
```

## 🧪 Testing Strategy

### **Unit Tests**
- Assignment creation with valid data
- Prevention of double assignments
- Assignment history tracking
- Fleet-based access control
- Assignment validation logic

### **Integration Tests**
- End-to-end assignment workflow
- Assignment with real database
- Manager authentication and authorization
- Assignment conflict resolution

### **Edge Cases**
- Assigning inactive driver/vehicle
- Cross-fleet assignment attempts
- Concurrent assignment attempts
- Assignment of already assigned resources

## 📊 Definition of Done

- [ ] All API endpoints implemented and tested
- [ ] Database schema created and migrated
- [ ] Assignment validation logic working
- [ ] Assignment history tracking functional
- [ ] Fleet-based access control enforced
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] Frontend interface updated
- [ ] Performance testing completed
- [ ] Security audit passed
- [ ] Code review approved

## 🔗 Dependencies

- **Prerequisite**: Story 1.4 (Manager Driver Registration) ✅ COMPLETED
- **Prerequisite**: Story 2.1 (Vehicle Registration) ✅ COMPLETED
- **Database**: PostgreSQL with UUID support
- **Authentication**: JWT-based manager authentication

## 🎯 Business Value

- **Operational Efficiency**: Clear driver-vehicle assignments improve fleet management
- **Accountability**: Track which driver is responsible for which vehicle
- **Compliance**: Maintain audit trail for regulatory requirements
- **Planning**: Enable better trip planning and resource allocation
- **Analytics**: Support fleet utilization and performance reporting

## 📝 Implementation Notes

- Use database constraints to prevent double assignments
- Implement soft deletes for assignment history
- Consider time-based assignments for future enhancement
- Ensure atomic operations for assignment changes
- Log all assignment changes for audit purposes

---

**Story Owner**: Fleet Management Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Fleet Managers, Operations Team
