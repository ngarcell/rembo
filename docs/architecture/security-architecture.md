# Security Architecture

## Authentication & Authorization

### JWT Token Structure
```json
{
  "sub": "user-uuid",
  "role": "passenger|manager|admin",
  "fleet_id": "fleet-uuid",
  "exp": 1640995200,
  "iat": 1640908800
}
```

### Role-Based Access Control (RBAC)
* **Admin**: Full system access, multi-tenant management
* **Manager**: Fleet-specific access, driver and vehicle management
* **Passenger**: Personal bookings and trip tracking only

### API Security
* All endpoints require valid JWT tokens
* Rate limiting: 100 requests/minute per user
* CORS configured for specific domains only
* Request/response logging for audit trails

## Data Protection

### Encryption
* **At Rest**: Database encryption via Supabase
* **In Transit**: TLS 1.3 for all API communications
* **Sensitive Fields**: GPS API keys encrypted with AES-256
* **PII**: Phone numbers and personal data encrypted

### Privacy Compliance
* Data retention policies (GPS data: 90 days, payment data: 7 years)
* User data export capabilities (GDPR compliance)
* Right to deletion implementation
* Consent management for data processing
