# Story 1.1: Passenger Registration

**Epic**: Epic 1 - User Authentication & Account Management  
**Story ID**: US1.1  
**Priority**: P0 (Critical)  
**Story Points**: 5  
**Status**: ✅ COMPLETED

## User Story
**As a passenger, I want to sign up using my phone number so that I can access the booking system**

## Acceptance Criteria
- [x] User can enter phone number in international format
- [x] System sends OTP via SMS for verification  
- [x] User can complete registration with OTP verification
- [x] System creates passenger profile with basic information
- [x] User receives welcome message upon successful registration

## Technical Requirements
- [x] Integrate with Supabase Auth phone authentication
- [x] Implement OTP verification flow
- [x] Create user profile in database with passenger role
- [x] Handle duplicate phone number scenarios

## Implementation Details

### API Endpoints
- `POST /api/v1/auth/register/initiate` - Initiate registration with phone number
- `POST /api/v1/auth/register/verify` - Verify OTP and complete registration
- `POST /api/v1/auth/register/resend` - Resend OTP if needed

### Database Schema
- **Supabase Auth**: User authentication records
- **Supabase Profiles**: User profile data with RLS policies
- **Local PostgreSQL**: User profiles for local development

### Security Features
- Cryptographically secure OTP generation using `secrets` module
- Rate limiting for registration attempts
- Phone number validation and normalization
- Duplicate phone number prevention

### Integration Points
- **Supabase Auth**: User creation and phone verification
- **Supabase Database**: Profile storage with Row Level Security
- **SMS Service**: OTP delivery (mocked in development)
- **Redis**: OTP storage and rate limiting

## Testing Results
✅ **Registration Flow Tested Successfully**
- Phone: +254700123457
- User: Jane Smith (jane.smith@example.com)
- Supabase Auth ID: 2ce3e794-c0be-407b-a801-bdb6dd0cf905
- Supabase Profile ID: a7161f7c-b48e-43ea-b3df-740c23721ce1
- Local Profile ID: 41775181-978c-4923-875b-27ee1d8a8afe

## Definition of Done
- [x] API endpoints implemented and tested
- [x] Database integration working with Supabase
- [x] OTP generation and verification secure
- [x] Error handling for all edge cases
- [x] Rate limiting implemented
- [x] Integration tests passing
- [x] Security scan passing (Bandit)
- [x] Code formatting applied (Black)
- [x] Documentation updated

## Dependencies
- ✅ Supabase project setup and configuration
- ✅ Database schema with RLS policies
- ✅ SMS service integration (mocked)
- ✅ Redis for session management

## Notes
- SMS service is currently mocked for development
- Real SMS integration with Africa's Talking ready for production
- Full end-to-end testing completed with real Supabase database
- CI/CD pipeline passing all checks
