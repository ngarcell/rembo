# Story 2.3: Vehicle Status & Maintenance Tracking

**Epic**: Epic 2 - Fleet & Vehicle Management  
**Story ID**: 2.3  
**Priority**: P1 (High)  
**Estimated Effort**: 8 Story Points  
**Status**: ✅ COMPLETED

## 📋 Story Description

**As a manager, I want to track vehicle status and maintenance history so that I can ensure fleet safety, compliance, and optimal operational efficiency.**

## 🎯 Acceptance Criteria

### ✅ **Vehicle Status Management**
- [x] Manager can view real-time status of all fleet vehicles
- [x] Vehicle status includes: Active, Maintenance, Out of Service, Inspection Due
- [x] Status changes are logged with timestamps and reasons
- [x] Automated status updates based on maintenance schedules
- [x] Status affects vehicle availability for trip assignments

### ✅ **Maintenance Tracking**
- [x] Manager can record maintenance activities
- [x] System tracks maintenance history per vehicle
- [x] Maintenance types: Routine, Repair, Inspection, Emergency
- [x] Cost tracking for maintenance activities
- [x] Maintenance reminders based on mileage/time intervals

### ✅ **Compliance & Safety**
- [x] Track vehicle inspection dates and certificates
- [x] Insurance expiry tracking and alerts
- [x] License renewal reminders
- [x] Safety incident recording and tracking
- [x] Compliance status dashboard

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Vehicle status enum
CREATE TYPE vehicle_status AS ENUM (
    'active', 'maintenance', 'out_of_service', 'inspection_due', 'retired'
);

-- Maintenance type enum
CREATE TYPE maintenance_type AS ENUM (
    'routine', 'repair', 'inspection', 'emergency', 'upgrade'
);

-- Vehicle status history
CREATE TABLE vehicle_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    previous_status vehicle_status,
    new_status vehicle_status NOT NULL,
    changed_by UUID NOT NULL REFERENCES user_profiles(id),
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT NOW(),
    fleet_id UUID NOT NULL REFERENCES fleets(id)
);

-- Maintenance records
CREATE TABLE vehicle_maintenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    maintenance_type maintenance_type NOT NULL,
    description TEXT NOT NULL,
    cost DECIMAL(10,2),
    service_provider VARCHAR(255),
    scheduled_date DATE,
    completed_date DATE,
    next_service_date DATE,
    mileage_at_service INTEGER,
    performed_by UUID REFERENCES user_profiles(id),
    notes TEXT,
    receipt_url VARCHAR(500),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle documents (insurance, inspection certificates)
CREATE TABLE vehicle_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- 'insurance', 'inspection', 'license'
    document_number VARCHAR(100),
    issue_date DATE,
    expiry_date DATE,
    issuing_authority VARCHAR(255),
    document_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add status to vehicles table
ALTER TABLE vehicles ADD COLUMN status vehicle_status DEFAULT 'active';
ALTER TABLE vehicles ADD COLUMN last_maintenance_date DATE;
ALTER TABLE vehicles ADD COLUMN next_maintenance_date DATE;
ALTER TABLE vehicles ADD COLUMN current_mileage INTEGER DEFAULT 0;
```

### **API Endpoints**
- `GET /api/v1/manager/vehicles/{id}/status` - Get vehicle status and history
- `PUT /api/v1/manager/vehicles/{id}/status` - Update vehicle status
- `POST /api/v1/manager/vehicles/{id}/maintenance` - Record maintenance activity
- `GET /api/v1/manager/vehicles/{id}/maintenance` - Get maintenance history
- `POST /api/v1/manager/vehicles/{id}/documents` - Upload vehicle document
- `GET /api/v1/manager/vehicles/{id}/documents` - Get vehicle documents
- `GET /api/v1/manager/fleet/status-dashboard` - Fleet status overview
- `GET /api/v1/manager/fleet/maintenance-alerts` - Get maintenance alerts

## 🧪 Testing Strategy

### **Unit Tests**
- Status change validation and logging
- Maintenance record creation and retrieval
- Document management functionality
- Alert generation logic
- Cost calculation and tracking

### **Integration Tests**
- End-to-end status management workflow
- Maintenance scheduling and tracking
- Document upload and retrieval
- Dashboard data aggregation
- Alert notification system

## 📊 Definition of Done

- [x] Vehicle status tracking implemented
- [x] Maintenance history system functional
- [x] Document management working
- [x] Status dashboard operational
- [x] Alert system implemented
- [x] All tests passing
- [x] API documentation complete
- [ ] Frontend interface updated

## 🔗 Dependencies

- **Prerequisite**: Story 2.1 (Vehicle Registration) ✅ COMPLETED
- **File Storage**: For document uploads
- **Notification System**: For maintenance alerts

## 🎯 Business Value

- **Safety**: Ensure vehicles are properly maintained and safe
- **Compliance**: Track regulatory requirements and deadlines
- **Cost Control**: Monitor maintenance costs and optimize spending
- **Efficiency**: Prevent breakdowns through proactive maintenance
- **Analytics**: Generate insights on fleet performance and costs

---

**Story Owner**: Fleet Management Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Fleet Managers, Maintenance Team, Compliance Officer
