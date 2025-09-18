# Technology Stack

## Frontend Technologies
* **Framework**: React 18+ with TypeScript
* **Build Tool**: Vite for fast development and optimized builds
* **PWA**: Service Workers for offline capability and app-like experience
* **State Management**: Zustand for lightweight state management
* **UI Components**: Tailwind CSS + Headless UI for consistent design
* **Maps**: Mapbox GL JS for interactive mapping and GPS visualization
* **Real-time**: Supabase Realtime client for WebSocket connections

## Backend Technologies
* **Runtime**: Python 3.11+
* **Framework**: FastAPI for high-performance async APIs
* **Database**: PostgreSQL via Supabase
* **Authentication**: Supabase Auth with JWT tokens
* **Real-time**: Supabase Realtime for WebSocket subscriptions
* **Task Queue**: Celery with Redis for background job processing
* **API Documentation**: OpenAPI/Swagger auto-generated from FastAPI

## External Services
* **Payment Processing**: M-Pesa Daraja API (Safaricom)
* **GPS Tracking**: Configurable GPS provider APIs (primary + fallback)
* **Mapping**: Mapbox for map rendering and geocoding
* **SMS Notifications**: Africa's Talking API for SMS alerts
* **Email**: SendGrid for transactional emails

## Infrastructure & DevOps
* **Containerization**: Docker with multi-stage builds
* **Orchestration**: Docker Compose for local development
* **Deployment**: Render.com for production hosting
* **CI/CD**: GitHub Actions for automated testing and deployment
* **Monitoring**: Sentry for error tracking, Render metrics for performance
* **Secrets Management**: Environment variables with Render's secret management
