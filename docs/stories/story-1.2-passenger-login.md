# Story 1.2: Passenger Login

**Epic**: Epic 1 - User Authentication & Account Management  
**Story ID**: US1.2  
**Priority**: P0 (Critical)  
**Story Points**: 5  
**Status**: 🔄 IN PROGRESS

## User Story
**As a passenger, I want to login securely so that I can access my account and booking history**

## Acceptance Criteria
- [ ] User can login with phone number and OTP
- [ ] System maintains secure session with JWT tokens
- [ ] User can access personalized dashboard after login
- [ ] System handles session expiry gracefully
- [ ] User can logout securely

## Technical Requirements
- [ ] Implement secure JWT token management
- [ ] Create session management middleware
- [ ] Handle token refresh automatically
- [ ] Implement secure logout functionality

## Implementation Plan

### Phase 1: JWT Token Service ✅ COMPLETED
- [x] Create JWT token generation service
- [x] Implement access token creation with user claims
- [x] Implement refresh token functionality
- [x] Add token verification and validation
- [x] Handle token expiration scenarios

### Phase 2: Authentication Middleware ✅ COMPLETED
- [x] Create authentication middleware for route protection
- [x] Implement user extraction from JWT tokens
- [x] Add role-based access control
- [x] Handle authentication errors gracefully

### Phase 3: Login Endpoints 🔄 IN PROGRESS
- [ ] Create login initiation endpoint
- [ ] Implement OTP-based login verification
- [ ] Add token refresh endpoint
- [ ] Create secure logout endpoint

### Phase 4: Protected Routes
- [ ] Add user profile endpoints
- [ ] Implement profile update functionality
- [ ] Create user dashboard data endpoints
- [ ] Add session management endpoints

## API Endpoints (Planned)
- `POST /api/v1/auth/login/initiate` - Start login with phone number
- `POST /api/v1/auth/login/verify` - Verify OTP and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Secure logout
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/profile` - Update user profile

## Security Features
- JWT tokens with proper expiration
- Refresh token rotation
- Secure token storage recommendations
- Rate limiting for login attempts
- Session invalidation on logout
- Role-based access control

## Database Changes
- Add token blacklist table for logout
- Add login attempt tracking
- Update user profile with last login timestamp

## Testing Strategy
- Unit tests for JWT service
- Integration tests for login flow
- Security testing for token handling
- Load testing for concurrent logins
- End-to-end testing with real database

## Definition of Done
- [ ] All API endpoints implemented and tested
- [ ] JWT token management working securely
- [ ] Authentication middleware protecting routes
- [ ] Login flow working end-to-end
- [ ] Token refresh working automatically
- [ ] Logout functionality secure
- [ ] Integration tests passing
- [ ] Security scan passing
- [ ] Documentation updated
- [ ] CI/CD pipeline passing

## Dependencies
- ✅ Story 1.1 (Passenger Registration) completed
- ✅ JWT service implementation
- ✅ Authentication middleware
- [ ] Frontend login components
- [ ] Session management on client side

## Risks & Mitigation
- **Risk**: JWT token security vulnerabilities
  - **Mitigation**: Use industry best practices, short expiration times
- **Risk**: Session management complexity
  - **Mitigation**: Implement proper token refresh flow
- **Risk**: Concurrent login handling
  - **Mitigation**: Proper database locking and rate limiting

## Notes
- Building on successful registration flow from Story 1.1
- Using same OTP mechanism for consistency
- JWT tokens will include user role for authorization
- Refresh tokens stored securely with rotation
