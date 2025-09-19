# Story 1.3: Admin Account Management

**Epic**: Epic 1 - User Authentication & Account Management  
**Story ID**: US1.3  
**Priority**: P1 (High)  
**Story Points**: 5  
**Status**: 📋 NOT STARTED

## User Story
**As an admin, I want to manage manager accounts so that I can control system access**

## Acceptance Criteria
- [ ] Admin can create new manager accounts
- [ ] Admin can view list of all managers
- [ ] Admin can activate/deactivate manager accounts
- [ ] Admin can assign managers to specific fleets
- [ ] Admin can reset manager passwords/access

## Technical Requirements
- [ ] Implement admin-only endpoints for user management
- [ ] Create manager account creation workflow
- [ ] Implement role-based access control middleware
- [ ] Add audit logging for admin actions

## Implementation Plan

### Phase 1: Admin Authentication
- [ ] Extend JWT middleware for admin role checking
- [ ] Create admin-only route decorators
- [ ] Implement admin session management
- [ ] Add admin role validation

### Phase 2: Manager Account Creation
- [ ] Create manager registration endpoint (admin-only)
- [ ] Implement manager profile creation
- [ ] Generate temporary manager credentials
- [ ] Send manager onboarding notifications

### Phase 3: Manager Account Management
- [ ] List all managers endpoint
- [ ] Manager account activation/deactivation
- [ ] Manager profile update by admin
- [ ] Manager password reset functionality

### Phase 4: Fleet Assignment
- [ ] Create fleet management system
- [ ] Implement manager-fleet assignment
- [ ] Add fleet-based access control
- [ ] Manager fleet transfer functionality

### Phase 5: Audit Logging
- [ ] Create audit log table
- [ ] Log all admin actions
- [ ] Implement audit trail viewing
- [ ] Add audit log filtering and search

## API Endpoints (Planned)
- `POST /api/v1/admin/managers` - Create new manager account
- `GET /api/v1/admin/managers` - List all managers
- `GET /api/v1/admin/managers/{id}` - Get manager details
- `PUT /api/v1/admin/managers/{id}` - Update manager account
- `POST /api/v1/admin/managers/{id}/activate` - Activate manager
- `POST /api/v1/admin/managers/{id}/deactivate` - Deactivate manager
- `POST /api/v1/admin/managers/{id}/reset-access` - Reset manager access
- `POST /api/v1/admin/managers/{id}/assign-fleet` - Assign to fleet
- `GET /api/v1/admin/audit-logs` - View audit logs

## Database Schema Changes
- Create `fleets` table
- Create `manager_fleet_assignments` table
- Create `audit_logs` table
- Add fleet_id to manager profiles
- Add admin-specific fields to user profiles

## Security Features
- Admin role verification for all endpoints
- Audit logging for all admin actions
- Secure manager credential generation
- Fleet-based access isolation
- Admin session timeout controls

## Testing Strategy
- Unit tests for admin role checking
- Integration tests for manager creation flow
- Security tests for admin-only access
- Audit log verification tests
- Fleet assignment functionality tests

## Definition of Done
- [ ] All admin endpoints implemented and secured
- [ ] Manager account lifecycle working
- [ ] Fleet assignment system operational
- [ ] Audit logging capturing all actions
- [ ] Role-based access control enforced
- [ ] Integration tests passing
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] CI/CD pipeline passing

## Dependencies
- ✅ Story 1.1 (Passenger Registration) completed
- ✅ Story 1.2 (Passenger Login) completed
- [ ] Fleet management system design
- [ ] Admin user interface components
- [ ] Manager onboarding workflow

## Risks & Mitigation
- **Risk**: Admin privilege escalation
  - **Mitigation**: Strict role validation and audit logging
- **Risk**: Manager account security
  - **Mitigation**: Secure credential generation and forced password change
- **Risk**: Fleet assignment conflicts
  - **Mitigation**: Database constraints and validation rules

## Notes
- Admin accounts will be created manually in production
- Manager accounts created through admin interface only
- Fleet system will be foundational for driver management
- Audit logs essential for compliance and security
