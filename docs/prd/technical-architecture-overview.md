# Technical Architecture Overview

## System Architecture
* **Frontend**: React-based Progressive Web App (PWA) for passengers, responsive web dashboards for managers/admins
* **Backend**: Python FastAPI microservices architecture with service separation
* **Database**: Supabase PostgreSQL with real-time subscriptions
* **Authentication**: Supabase Auth with role-based access control
* **External Integrations**: M-Pesa Daraja API, third-party GPS APIs, Mapbox mapping
* **Infrastructure**: Docker containerization, Render deployment platform, CI/CD pipelines

## Service Architecture
* **Auth Service**: User authentication and authorization
* **Fleet Service**: Vehicle and driver management
* **Booking Service**: Trip creation and seat reservation
* **Payment Service**: M-Pesa integration and transaction processing
* **GPS Service**: Location tracking and real-time updates
* **Reporting Service**: Analytics and report generation
* **Notification Service**: Real-time updates and alerts

## Data Flow
* **GPS Data**: Vehicles → GPS API → GPS Service → Supabase Realtime → Client Applications
* **Booking Flow**: Passenger App → Booking Service → Database → Payment Service → M-Pesa API
* **Real-time Updates**: Database Changes → Supabase Realtime → WebSocket → Client Applications
