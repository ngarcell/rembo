# AI-Powered Matatu Fleet Management & Route Optimization System Architecture Document

## Introduction

This document outlines the overall project architecture for the AI-Powered Matatu Fleet Management & Route Optimization System, including backend systems, shared services, and frontend components. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

The architecture is designed to support a multi-tenant SaaS platform that serves three distinct user types (Admins, Managers, Passengers) with real-time GPS tracking, payment processing, and fleet management capabilities.

### Starter Template or Existing Project

This is a greenfield project that will be built from scratch using modern web technologies. No existing starter template will be used, allowing for custom architecture optimized for the specific requirements of matatu fleet management.

## System Overview

### Architecture Principles

* **Microservices Architecture**: Decomposed into focused, independently deployable services
* **Event-Driven Design**: Asynchronous communication between services using events
* **API-First Approach**: All services expose well-defined REST APIs
* **Real-time Capabilities**: WebSocket connections for live GPS tracking and notifications
* **Security by Design**: Authentication, authorization, and data encryption at every layer
* **Scalability**: Horizontal scaling capabilities for high-traffic scenarios
* **Observability**: Comprehensive logging, monitoring, and tracing

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Passenger     │    │    Manager      │    │     Admin       │
│     PWA         │    │   Dashboard     │    │    Dashboard    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (Load Balancer)│
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Fleet Service  │    │ Booking Service │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Supabase      │
                    │  (Database +    │
                    │   Realtime)     │
                    └─────────────────┘
```

## Technology Stack

### Frontend Technologies
* **Framework**: React 18+ with TypeScript
* **Build Tool**: Vite for fast development and optimized builds
* **PWA**: Service Workers for offline capability and app-like experience
* **State Management**: Zustand for lightweight state management
* **UI Components**: Tailwind CSS + Headless UI for consistent design
* **Maps**: Mapbox GL JS for interactive mapping and GPS visualization
* **Real-time**: Supabase Realtime client for WebSocket connections

### Backend Technologies
* **Runtime**: Python 3.11+
* **Framework**: FastAPI for high-performance async APIs
* **Database**: PostgreSQL via Supabase
* **Authentication**: Supabase Auth with JWT tokens
* **Real-time**: Supabase Realtime for WebSocket subscriptions
* **Task Queue**: Celery with Redis for background job processing
* **API Documentation**: OpenAPI/Swagger auto-generated from FastAPI

### External Services
* **Payment Processing**: M-Pesa Daraja API (Safaricom)
* **GPS Tracking**: Configurable GPS provider APIs (primary + fallback)
* **Mapping**: Mapbox for map rendering and geocoding
* **SMS Notifications**: Africa's Talking API for SMS alerts
* **Email**: SendGrid for transactional emails

### Infrastructure & DevOps
* **Containerization**: Docker with multi-stage builds
* **Orchestration**: Docker Compose for local development
* **Deployment**: Render.com for production hosting
* **CI/CD**: GitHub Actions for automated testing and deployment
* **Monitoring**: Sentry for error tracking, Render metrics for performance
* **Secrets Management**: Environment variables with Render's secret management

## Service Architecture

### Core Services

#### 1. Authentication Service
**Responsibility**: User authentication, authorization, and session management

**Key Features**:
* Phone number-based registration and login
* JWT token generation and validation
* Role-based access control (Admin, Manager, Passenger)
* Session management and token refresh

**Technology**: Supabase Auth with custom policies

#### 2. Fleet Management Service
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

#### 3. Booking Service
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

#### 4. Payment Service
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

#### 5. GPS Tracking Service
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

#### 6. Notification Service
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

#### 7. Reporting Service
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

## Database Design

### Database Schema Overview

The system uses PostgreSQL via Supabase with the following core tables:

#### User Management Tables
```sql
-- Users table (managed by Supabase Auth)
users (
  id UUID PRIMARY KEY,
  phone VARCHAR(15) UNIQUE NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User profiles for additional information
user_profiles (
  id UUID PRIMARY KEY REFERENCES users(id),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255),
  is_active BOOLEAN DEFAULT true
);
```

#### Fleet Management Tables
```sql
-- Fleet organizations
fleets (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  manager_id UUID REFERENCES users(id),
  fleet_code VARCHAR(10) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Vehicles
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

-- Drivers
drivers (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  driver_code VARCHAR(20) UNIQUE NOT NULL,
  license_number VARCHAR(50) NOT NULL,
  fleet_id UUID REFERENCES fleets(id),
  is_active BOOLEAN DEFAULT true
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

#### Booking & Trip Tables
```sql
-- Routes
routes (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  origin VARCHAR(255) NOT NULL,
  destination VARCHAR(255) NOT NULL,
  distance_km DECIMAL(8,2),
  estimated_duration_minutes INTEGER,
  base_fare DECIMAL(10,2) NOT NULL
);

-- Trips
trips (
  id UUID PRIMARY KEY,
  route_id UUID REFERENCES routes(id),
  vehicle_id UUID REFERENCES vehicles(id),
  driver_id UUID REFERENCES drivers(id),
  scheduled_departure TIMESTAMP NOT NULL,
  actual_departure TIMESTAMP,
  scheduled_arrival TIMESTAMP,
  actual_arrival TIMESTAMP,
  status trip_status DEFAULT 'scheduled',
  fare DECIMAL(10,2) NOT NULL,
  available_seats INTEGER NOT NULL
);

-- Bookings
bookings (
  id UUID PRIMARY KEY,
  trip_id UUID REFERENCES trips(id),
  passenger_id UUID REFERENCES users(id),
  seats_booked INTEGER NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  booking_status booking_status DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### Payment Tables
```sql
-- Payments
payments (
  id UUID PRIMARY KEY,
  booking_id UUID REFERENCES bookings(id),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'KES',
  payment_method VARCHAR(50) DEFAULT 'mpesa',
  mpesa_transaction_id VARCHAR(100),
  status payment_status DEFAULT 'pending',
  initiated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Payment receipts
receipts (
  id UUID PRIMARY KEY,
  payment_id UUID REFERENCES payments(id),
  receipt_number VARCHAR(50) UNIQUE NOT NULL,
  receipt_data JSONB NOT NULL,
  generated_at TIMESTAMP DEFAULT NOW()
);
```

#### GPS & Location Tables
```sql
-- GPS locations
gps_locations (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  altitude DECIMAL(8, 2),
  speed DECIMAL(5, 2),
  heading DECIMAL(5, 2),
  accuracy DECIMAL(5, 2),
  recorded_at TIMESTAMP NOT NULL,
  received_at TIMESTAMP DEFAULT NOW()
);

-- Location history (partitioned by date)
location_history (
  id UUID PRIMARY KEY,
  vehicle_id UUID REFERENCES vehicles(id),
  trip_id UUID REFERENCES trips(id),
  route_data JSONB NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  total_distance_km DECIMAL(8, 2),
  created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);
```

### Database Optimization

#### Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_vehicles_fleet_id ON vehicles(fleet_id);
CREATE INDEX idx_trips_vehicle_date ON trips(vehicle_id, scheduled_departure);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);
CREATE INDEX idx_gps_vehicle_time ON gps_locations(vehicle_id, recorded_at DESC);
CREATE INDEX idx_payments_booking ON payments(booking_id);

-- Composite indexes for common queries
CREATE INDEX idx_trips_route_status_date ON trips(route_id, status, scheduled_departure);
CREATE INDEX idx_bookings_trip_status ON bookings(trip_id, booking_status);
```

#### Row Level Security (RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Example policies
CREATE POLICY "Managers can view their fleet vehicles" ON vehicles
  FOR SELECT USING (
    fleet_id IN (
      SELECT id FROM fleets WHERE manager_id = auth.uid()
    )
  );

CREATE POLICY "Passengers can view their bookings" ON bookings
  FOR SELECT USING (passenger_id = auth.uid());
```

## Security Architecture

### Authentication & Authorization

#### JWT Token Structure
```json
{
  "sub": "user-uuid",
  "role": "passenger|manager|admin",
  "fleet_id": "fleet-uuid",
  "exp": 1640995200,
  "iat": 1640908800
}
```

#### Role-Based Access Control (RBAC)
* **Admin**: Full system access, multi-tenant management
* **Manager**: Fleet-specific access, driver and vehicle management
* **Passenger**: Personal bookings and trip tracking only

#### API Security
* All endpoints require valid JWT tokens
* Rate limiting: 100 requests/minute per user
* CORS configured for specific domains only
* Request/response logging for audit trails

### Data Protection

#### Encryption
* **At Rest**: Database encryption via Supabase
* **In Transit**: TLS 1.3 for all API communications
* **Sensitive Fields**: GPS API keys encrypted with AES-256
* **PII**: Phone numbers and personal data encrypted

#### Privacy Compliance
* Data retention policies (GPS data: 90 days, payment data: 7 years)
* User data export capabilities (GDPR compliance)
* Right to deletion implementation
* Consent management for data processing

## Deployment Architecture

### Environment Strategy
* **Development**: Local Docker Compose setup
* **Staging**: Render.com with reduced resources
* **Production**: Render.com with auto-scaling enabled

### Container Architecture
```dockerfile
# Multi-stage build for Python services
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CI/CD Pipeline
```yaml
# GitHub Actions workflow
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## Performance & Scalability

### Performance Targets
* **API Response Time**: <200ms for 95th percentile
* **GPS Update Latency**: <5 seconds end-to-end
* **Database Query Time**: <100ms for complex queries
* **Frontend Load Time**: <3 seconds on 3G connection

### Scaling Strategy
* **Horizontal Scaling**: Multiple service instances behind load balancer
* **Database Scaling**: Read replicas for reporting queries
* **Caching**: Redis for frequently accessed data
* **CDN**: Static assets served via Render's CDN

### Monitoring & Observability
* **Application Metrics**: Custom metrics via Prometheus
* **Error Tracking**: Sentry for exception monitoring
* **Performance Monitoring**: APM via Render's built-in tools
* **Log Aggregation**: Structured logging with correlation IDs
