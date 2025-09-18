# Epic 2: Fleet & Vehicle Management

**Epic Goal**: Provide comprehensive tools for managing vehicles, drivers, and their assignments

## Overview
This epic implements the core fleet management functionality that allows managers to register vehicles, manage driver profiles, and handle vehicle-driver assignments. It provides the operational foundation for tracking and managing matatu fleets effectively.

## User Stories

### US2.1: Vehicle Registration
**As a manager, I want to register vehicles with complete details so that I can track my fleet**

**Acceptance Criteria:**
- Manager can register vehicles with all required details
- System validates license plate uniqueness
- GPS device integration configured during registration
- Vehicle capacity and specifications recorded
- Vehicle status tracking initialized

**Technical Requirements:**
- Create vehicle registration API endpoints
- Implement license plate validation and uniqueness checks
- Add GPS device configuration fields
- Create vehicle profile management interface
- Implement fleet-based vehicle organization

**Required Fields:**
- Fleet Number
- License Plate (unique)
- Vehicle Capacity
- GPS Device ID
- SIM Number
- GPS API Key (encrypted)
- Vehicle Type/Model
- Registration Date

### US2.2: Driver-Vehicle Assignment
**As a manager, I want to assign drivers to vehicles so that I can manage operations**

**Acceptance Criteria:**
- Manager can assign any driver to any vehicle in their fleet
- System prevents double-assignment of vehicles
- Assignment history is maintained
- Manager can reassign drivers as needed
- System tracks assignment duration and changes

**Technical Requirements:**
- Create assignment management API
- Implement assignment validation logic
- Add assignment history tracking
- Create assignment management interface
- Handle assignment conflicts and validation

### US2.3: Vehicle Status & History
**As a manager, I want to view vehicle status and history so that I can make informed decisions**

**Acceptance Criteria:**
- Manager can view current status of all vehicles
- System shows vehicle location and activity
- Manager can access vehicle maintenance history
- Trip history and performance metrics available
- Vehicle utilization reports accessible

**Technical Requirements:**
- Create vehicle dashboard with real-time status
- Implement vehicle history tracking
- Add performance metrics calculation
- Create reporting interface for vehicle data
- Integrate with GPS tracking for live status

### US2.4: Vehicle-Driver Relationship Tracking
**As a system, I want to maintain vehicle-driver relationships so that operations are traceable**

**Acceptance Criteria:**
- System maintains complete assignment audit trail
- All trips linked to specific driver-vehicle combinations
- Assignment changes logged with timestamps
- Relationship data available for reporting
- Data integrity maintained across all operations

**Technical Requirements:**
- Implement comprehensive audit logging
- Create relationship tracking database schema
- Add data integrity constraints
- Implement relationship validation middleware
- Create audit trail reporting capabilities

## Definition of Done
- [ ] All vehicle registration workflows complete
- [ ] Driver-vehicle assignment system functional
- [ ] Vehicle status tracking operational
- [ ] Fleet management dashboard implemented
- [ ] Assignment history and audit trails working
- [ ] Integration tests passing
- [ ] Performance testing completed

## Dependencies
- Epic 1: Authentication (for manager roles)
- GPS provider API integration
- Database schema for fleet management
- Frontend fleet management interfaces

## Technical Architecture

### Database Schema
```sql
-- Vehicles table
vehicles (
  id UUID PRIMARY KEY,
  fleet_id UUID REFERENCES fleets(id),
  fleet_number VARCHAR(20) NOT NULL,
  license_plate VARCHAR(20) UNIQUE NOT NULL,
  capacity INTEGER NOT NULL,
  gps_device_id VARCHAR(100),
  sim_number VARCHAR(20),
  gps_api_key VARCHAR(255) ENCRYPTED,
  status vehicle_status DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle assignments
vehicle_assignments (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  driver_id UUID REFERENCES drivers(id),
  assigned_at TIMESTAMP DEFAULT NOW(),
  unassigned_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);
```

### API Endpoints
- `POST /api/fleet/vehicles` - Register new vehicle
- `GET /api/fleet/vehicles` - List vehicles with filtering
- `PUT /api/fleet/vehicles/{id}` - Update vehicle details
- `POST /api/fleet/assignments` - Create driver assignment
- `GET /api/fleet/assignments/history` - Get assignment history

## Risks & Mitigation
- **Risk**: GPS device integration complexity
  - **Mitigation**: Use standardized GPS APIs with fallback options
- **Risk**: Vehicle assignment conflicts
  - **Mitigation**: Implement atomic assignment operations with proper locking
- **Risk**: Data integrity issues with relationships
  - **Mitigation**: Use database constraints and validation middleware

## Estimated Effort
**Story Points**: 18
**Duration**: 2 sprints
**Priority**: P0 (Critical - Required for operational functionality)
