# Service Architecture

## Core Services

### 1. Authentication Service
**Responsibility**: User authentication, authorization, and session management

**Key Features**:
* Phone number-based registration and login
* JWT token generation and validation
* Role-based access control (Admin, Manager, Passenger)
* Session management and token refresh

**Technology**: Supabase Auth with custom policies

### 2. Fleet Management Service
**Responsibility**: Vehicle and driver management operations

**Key Features**:
* Vehicle registration and profile management
* Driver registration and assignment
* Fleet hierarchy and organization
* Vehicle status tracking and maintenance records

**API Endpoints**:
* `POST /api/fleet/vehicles` - Register new vehicle
* `GET /api/fleet/vehicles` - List vehicles with filtering
* `POST /api/fleet/drivers` - Register new driver
* `PUT /api/fleet/assignments` - Assign driver to vehicle

### 3. Booking Service
**Responsibility**: Trip creation, seat booking, and reservation management

**Key Features**:
* Trip scheduling and management
* Real-time seat inventory tracking
* Booking creation and confirmation
* Overbooking prevention with atomic operations

**API Endpoints**:
* `POST /api/bookings/trips` - Create new trip
* `GET /api/bookings/trips/available` - List available trips
* `POST /api/bookings/reservations` - Create seat reservation
* `GET /api/bookings/reservations/{id}` - Get booking details

### 4. Payment Service
**Responsibility**: Payment processing and financial transaction management

**Key Features**:
* M-Pesa STK Push integration
* Payment status tracking and webhooks
* Receipt generation and storage
* Refund processing for cancellations

**API Endpoints**:
* `POST /api/payments/initiate` - Start M-Pesa payment
* `POST /api/payments/callback` - M-Pesa webhook handler
* `GET /api/payments/{id}/status` - Check payment status
* `POST /api/payments/{id}/refund` - Process refund

### 5. GPS Tracking Service
**Responsibility**: Real-time location tracking and route management

**Key Features**:
* GPS data ingestion from multiple providers
* Real-time location broadcasting via WebSockets
* Route optimization and analysis
* Geofencing and location-based alerts

**API Endpoints**:
* `POST /api/gps/locations` - Receive GPS updates
* `GET /api/gps/vehicles/{id}/location` - Get current location
* `GET /api/gps/vehicles/{id}/history` - Get location history
* `POST /api/gps/geofences` - Create geofence alerts

### 6. Notification Service
**Responsibility**: Multi-channel communication and alerts

**Key Features**:
* Real-time push notifications via WebSockets
* SMS notifications for critical updates
* Email notifications for receipts and reports
* In-app notification management

**API Endpoints**:
* `POST /api/notifications/send` - Send notification
* `GET /api/notifications/user/{id}` - Get user notifications
* `PUT /api/notifications/{id}/read` - Mark as read

### 7. Reporting Service
**Responsibility**: Analytics, reporting, and business intelligence

**Key Features**:
* Real-time dashboard metrics
* CSV report generation and export
* Revenue and performance analytics
* Custom report builder for managers

**API Endpoints**:
* `GET /api/reports/dashboard` - Get dashboard metrics
* `POST /api/reports/generate` - Generate custom report
* `GET /api/reports/{id}/download` - Download report file
