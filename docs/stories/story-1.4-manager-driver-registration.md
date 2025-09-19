# Story 1.4: Manager Driver Registration

**Epic**: Epic 1 - User Authentication & Account Management  
**Story ID**: US1.4  
**Priority**: P1 (High)  
**Story Points**: 8  
**Status**: 📋 NOT STARTED

## User Story
**As a manager, I want to register drivers so that I can assign them to vehicles**

## Acceptance Criteria
- [ ] Manager can create driver profiles with personal details
- [ ] System auto-generates unique driver IDs
- [ ] Manager can upload driver license and documents
- [ ] Driver receives credentials to access system
- [ ] Manager can view all drivers in their fleet

## Technical Requirements
- [ ] Implement driver registration API endpoints
- [ ] Create unique driver ID generation algorithm
- [ ] Add file upload capability for documents
- [ ] Implement fleet-based access control

## Implementation Plan

### Phase 1: Driver Profile System
- [ ] Create driver profile database schema
- [ ] Implement driver profile model
- [ ] Add driver personal information fields
- [ ] Create driver profile validation

### Phase 2: Driver ID Generation
- [ ] Implement unique driver ID algorithm (DRV-XXXYYY)
- [ ] Create fleet-based numbering system
- [ ] Add database sequences for atomic generation
- [ ] Handle concurrent registration scenarios

### Phase 3: Document Management
- [ ] Create file upload service
- [ ] Implement document storage (Supabase Storage)
- [ ] Add document validation and processing
- [ ] Create document viewing and management

### Phase 4: Driver Account Creation
- [ ] Generate driver login credentials
- [ ] Create driver onboarding workflow
- [ ] Send driver welcome notifications
- [ ] Implement driver first-time login flow

### Phase 5: Fleet Management Integration
- [ ] Implement fleet-based driver access
- [ ] Add manager-driver relationship
- [ ] Create driver listing and filtering
- [ ] Add driver search functionality

## API Endpoints (Planned)
- `POST /api/v1/manager/drivers` - Register new driver
- `GET /api/v1/manager/drivers` - List fleet drivers
- `GET /api/v1/manager/drivers/{id}` - Get driver details
- `PUT /api/v1/manager/drivers/{id}` - Update driver profile
- `POST /api/v1/manager/drivers/{id}/documents` - Upload documents
- `GET /api/v1/manager/drivers/{id}/documents` - List driver documents
- `POST /api/v1/manager/drivers/{id}/activate` - Activate driver
- `POST /api/v1/manager/drivers/{id}/deactivate` - Deactivate driver

## Database Schema
```sql
-- Driver profiles table
CREATE TABLE driver_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id VARCHAR(20) UNIQUE NOT NULL, -- DRV-XXXYYY format
    user_id UUID REFERENCES auth.users(id),
    fleet_id UUID REFERENCES fleets(id),
    manager_id UUID REFERENCES user_profiles(id),
    
    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255),
    date_of_birth DATE,
    national_id VARCHAR(50),
    
    -- License Information
    license_number VARCHAR(50) UNIQUE NOT NULL,
    license_class VARCHAR(10) NOT NULL,
    license_expiry DATE NOT NULL,
    
    -- Employment Details
    hire_date DATE DEFAULT CURRENT_DATE,
    employment_status VARCHAR(20) DEFAULT 'active',
    
    -- System Fields
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Driver documents table
CREATE TABLE driver_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID REFERENCES driver_profiles(id),
    document_type VARCHAR(50) NOT NULL, -- license, id_copy, photo, etc.
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by UUID REFERENCES user_profiles(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Driver ID Generation Algorithm
- Format: `DRV-XXXYYY`
- XXX: Sequential driver number within fleet (001-999)
- YYY: Fleet identifier code (3 characters)
- Example: `DRV-001ABC`, `DRV-002ABC`, etc.

## File Upload Integration
- Use Supabase Storage for document storage
- Support multiple file formats (PDF, JPG, PNG)
- Implement file size limits and validation
- Create secure file access with signed URLs

## Security Features
- Manager can only register drivers in their fleet
- Driver documents encrypted at rest
- Secure file upload with virus scanning
- Driver credential generation with secure passwords
- Fleet-based access control for all operations

## Testing Strategy
- Unit tests for driver ID generation
- Integration tests for driver registration flow
- File upload functionality testing
- Fleet-based access control testing
- Concurrent registration scenario testing

## Definition of Done
- [ ] Driver registration flow working end-to-end
- [ ] Unique driver ID generation implemented
- [ ] Document upload and management working
- [ ] Fleet-based access control enforced
- [ ] Driver account creation automated
- [ ] Manager can view and manage fleet drivers
- [ ] Integration tests passing
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] CI/CD pipeline passing

## Dependencies
- ✅ Story 1.1 (Passenger Registration) completed
- ✅ Story 1.2 (Passenger Login) completed
- [ ] Story 1.3 (Admin Account Management) completed
- [ ] Fleet management system
- [ ] File upload service
- [ ] Document storage solution

## Risks & Mitigation
- **Risk**: Driver ID collision in concurrent scenarios
  - **Mitigation**: Use database sequences and proper locking
- **Risk**: Document storage security
  - **Mitigation**: Encrypted storage and secure access controls
- **Risk**: Large file uploads affecting performance
  - **Mitigation**: File size limits and background processing

## Notes
- Driver IDs must be unique across entire system
- Document storage will use Supabase Storage
- Driver accounts created automatically upon registration
- Fleet assignment is mandatory for all drivers
- Manager can only manage drivers in their assigned fleet
