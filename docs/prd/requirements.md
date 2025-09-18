# Requirements

## Functional Requirements

**Authentication & User Management**
* **FR1**: Users must be able to sign up and login using their phone number through Supabase Auth
* **FR2**: System must support role-based access control with three distinct user types: Admin, Manager, and Passenger
* **FR3**: Admins must be able to create, manage, and deactivate manager and passenger accounts
* **FR4**: System must auto-generate unique driver IDs in format `DRV-XXXYYY` where XXX is driver sequence and YYY is fleet identifier
* **FR5**: System must maintain user session management with secure token-based authentication

**Vehicle & Driver Management**
* **FR6**: Managers must be able to register vehicles with complete details including fleet number, license plate, capacity, GPS device ID, SIM number, and GPS API key
* **FR7**: Managers must be able to register and manage driver profiles with personal information and credentials
* **FR8**: System must support assignment of drivers to specific vehicles with tracking of assignment history
* **FR9**: System must automatically link driver IDs with fleet numbers for operational tracking
* **FR10**: System must maintain a comprehensive database of vehicle status, maintenance records, and operational history

**Booking & Trip Management**
* **FR11**: Passengers must be able to view available trips with real-time seat availability
* **FR12**: Passengers must be able to book seats for specific trips with immediate confirmation
* **FR13**: System must prevent overbooking by maintaining real-time seat inventory
* **FR14**: System must support trip creation and management by authorized managers
* **FR15**: System must track trip status (scheduled, in-progress, completed, cancelled)

**Payment Processing**
* **FR16**: System must integrate with M-Pesa Daraja API for payment processing using STK Push
* **FR17**: System must store payment confirmations and generate digital receipts
* **FR18**: System must handle payment failures gracefully with retry mechanisms
* **FR19**: System must support refund processing for cancelled trips
* **FR20**: System must maintain comprehensive payment audit trails

**GPS Tracking & Location Services**
* **FR21**: Vehicles must publish GPS coordinates in real-time via API/Webhook integration
* **FR22**: System must display live vehicle locations on interactive maps using Mapbox
* **FR23**: Passengers must be able to track their booked vehicle's location in real-time
* **FR24**: Managers must be able to monitor all fleet vehicles simultaneously on a unified dashboard
* **FR25**: System must maintain GPS history for route analysis and optimization

**Reporting & Analytics**
* **FR26**: Managers must be able to generate and export CSV reports for revenue, trips, and driver performance
* **FR27**: System must provide real-time dashboard analytics for key performance indicators
* **FR28**: Admins must have access to system-wide reporting across all fleets and managers
* **FR29**: System must track and report on trip completion rates, payment success rates, and customer satisfaction metrics

**Administrative Controls**
* **FR30**: Admins must be able to configure fare policies, route definitions, and system settings
* **FR31**: Admins must have emergency kill-switch capability to immediately block compromised vehicles or user accounts
* **FR32**: Managers must be able to approve or reject trip logs and driver reports
* **FR33**: System must maintain comprehensive audit logs of all administrative actions

## Non-Functional Requirements

**Performance & Scalability**
* **NFR1**: System must support minimum 10,000 concurrent users during peak hours
* **NFR2**: GPS location updates must have latency under 5 seconds from vehicle to passenger display
* **NFR3**: Booking operations must complete within 3 seconds under normal load
* **NFR4**: Payment processing must complete within 30 seconds including M-Pesa confirmation
* **NFR5**: System must maintain 99.9% uptime for critical booking and tracking services

**Security & Compliance**
* **NFR6**: All sensitive data including GPS API keys and payment information must be encrypted at rest and in transit
* **NFR7**: System must implement secure API authentication and authorization for all external integrations
* **NFR8**: Personal user data must be handled in compliance with applicable data protection regulations
* **NFR9**: System must implement rate limiting and DDoS protection for public-facing endpoints

**Reliability & Availability**
* **NFR10**: System must gracefully handle GPS device failures with appropriate fallback mechanisms
* **NFR11**: Payment system must have robust error handling for M-Pesa API failures
* **NFR12**: System must support offline capability for critical driver operations
* **NFR13**: Database must implement automated backup and disaster recovery procedures

**Technology & Integration**
* **NFR14**: Backend services must be built using Python FastAPI microservices architecture
* **NFR15**: Frontend must be implemented as React-based Progressive Web App (PWA) for passengers
* **NFR16**: Manager and admin interfaces must be responsive web applications
* **NFR17**: System must use Supabase for authentication, database, and real-time subscriptions
* **NFR18**: Deployment must support Docker containerization and CI/CD pipelines
* **NFR19**: System must integrate with third-party GPS APIs with configurable provider support
