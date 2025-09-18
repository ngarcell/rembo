# Rembo - Matatu Fleet Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A comprehensive platform for managing matatu fleets, bookings, and operations in Kenya. Built using the **BMAD METHOD™** (Agentic Agile Driven Development) framework for enterprise-grade reliability and scalability.

## 🚀 Features

### 🔐 Authentication & User Management
- **Phone-based Registration**: SMS OTP verification using Africa's Talking
- **Multi-role Support**: Admin, Manager, Passenger roles
- **Secure Authentication**: JWT tokens with refresh mechanism
- **Rate Limiting**: Protection against abuse and spam

### 🚌 Fleet Management
- **Vehicle Management**: Track vehicles, capacity, GPS devices
- **Driver Management**: Driver profiles, licenses, assignments
- **Fleet Organization**: Multi-fleet support with hierarchical management
- **Real-time GPS Tracking**: Integration with GPS devices

### 📱 Booking System
- **Trip Scheduling**: Create and manage scheduled trips
- **Seat Booking**: Real-time seat availability and booking
- **Payment Integration**: M-Pesa integration for seamless payments
- **Booking Management**: Cancellations, modifications, history

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Git

### Development Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd matatu-fleet-management
   cp .env.example .env
   # Edit .env with your configuration values
   ```

2. **Start development environment**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8080
   - Auth Service: http://localhost:8001
   - Fleet Service: http://localhost:8002
   - Booking Service: http://localhost:8003

## 🏗️ Architecture

### Microservices
- **Auth Service** (Port 8001): User authentication and authorization
- **Fleet Service** (Port 8002): Vehicle and driver management
- **Booking Service** (Port 8003): Trip booking and management
- **Payment Service** (Port 8004): M-Pesa payment processing
- **GPS Service** (Port 8005): Real-time location tracking
- **Notification Service** (Port 8006): Multi-channel notifications
- **Reporting Service** (Port 8007): Analytics and reporting

### Frontend
- **Passenger PWA**: React-based Progressive Web App
- **Manager Dashboard**: Web-based fleet management interface
- **Admin Panel**: System administration interface

## 📋 BMAD Development Workflow

This project follows the BMAD METHOD™ for structured AI-driven development:

### Planning Phase ✅ Complete
- [x] Project Brief created
- [x] Comprehensive PRD with 33 functional requirements
- [x] Technical Architecture document
- [x] Master Checklist validation
- [x] Document sharding into 7 epics

### Development Phase 🚧 In Progress
- [ ] Epic 1: User Authentication & Account Management
- [ ] Epic 2: Fleet & Vehicle Management
- [ ] Epic 3: Booking & Trip Management
- [ ] Epic 4: Payment Processing
- [ ] Epic 5: GPS Tracking & Location Services
- [ ] Epic 6: Reporting & Analytics
- [ ] Epic 7: Administrative Controls

## 📁 Project Structure

```
├── docs/                    # BMAD planning documents
│   ├── prd/                # Product Requirements (sharded)
│   ├── architecture/       # Technical Architecture (sharded)
│   ├── epics/              # Development epics
│   └── stories/            # Implementation stories
├── backend/
│   ├── services/           # Microservices
│   │   ├── auth/
│   │   ├── fleet/
│   │   ├── booking/
│   │   └── ...
│   └── shared/             # Shared utilities
├── frontend/               # React PWA
├── infrastructure/         # Docker, Nginx configs
└── tests/                  # Test suites
```

## 🛠️ Development Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Run tests
docker-compose exec [service-name] pytest

# Database migrations
docker-compose exec postgres psql -U postgres -d matatu_fleet

# Stop all services
docker-compose down
```

## 🔧 Configuration

Key environment variables (see `.env.example`):
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`: Supabase configuration
- `MPESA_*`: M-Pesa Daraja API credentials
- `MAPBOX_TOKEN`: Mapbox access token
- `GPS_API_*`: GPS provider configuration

## 📊 Key Features

### For Passengers
- Phone number registration and login
- Real-time trip search and booking
- M-Pesa payment integration
- Live vehicle tracking
- Trip history and receipts

### For Fleet Managers
- Vehicle and driver management
- Trip scheduling and monitoring
- Revenue tracking and reporting
- Real-time fleet visibility

### For Administrators
- Multi-tenant fleet management
- System configuration and settings
- Comprehensive analytics and reporting
- Emergency controls and audit trails

## 🧪 Testing

- **Unit Tests**: Each service has comprehensive unit tests
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Critical user journey testing
- **Load Tests**: Performance and scalability testing

## 📈 Monitoring & Observability

- **Logging**: Structured logging with correlation IDs
- **Metrics**: Custom metrics via Prometheus
- **Error Tracking**: Sentry integration
- **Performance**: APM monitoring

## 🚀 Deployment

Production deployment uses:
- **Platform**: Render.com
- **Database**: Supabase PostgreSQL
- **CDN**: Render's built-in CDN
- **CI/CD**: GitHub Actions

## 📝 Contributing

This project follows BMAD METHOD™ development practices:
1. All changes must align with PRD requirements
2. Follow the SM/Dev/QA cycle for new features
3. Maintain comprehensive test coverage
4. Update documentation with changes

## 📄 License

[License information]

---

Built with ❤️ using BMAD METHOD™ for AI-driven development
