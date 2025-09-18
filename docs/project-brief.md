# 📄 Project Brief

**AI-Powered Matatu Fleet Management & Route Optimization System**

## Project Overview

Kenya's matatu industry relies heavily on manual operations, which limits efficiency, transparency, and customer experience. This system modernizes operations with digital booking, GPS-based fleet tracking, integrated payments, and AI-powered optimization.

## Goals

* Digitize matatu fleet operations with real-time visibility and control
* Enable seat booking and fare payment via M-Pesa
* Optimize routes and fleet usage with AI
* Provide tools for administrators and managers to handle drivers, vehicles, and trips
* Deliver actionable reports and insights for business intelligence

## Target Users

1. **Admin**
   * Manages all accounts (managers, drivers, passengers)
   * Configures fare policies, routes, and system settings
   * Full access to reports and kill-switch for compromised assets

2. **Manager**
   * Registers and manages drivers & vehicles
   * Assigns drivers to vehicles
   * Monitors trips, vehicle locations, and revenue
   * Exports reports (CSV)

3. **User (Passenger)**
   * Signs up with phone number
   * Books seats for trips
   * Pays via M-Pesa STK Push
   * Views live bus locations, trip history, and receipts

## Key Features

### Authentication & Accounts
* Users sign up/login via phone number (Supabase Auth)
* Admins manage manager/user accounts
* Unique IDs auto-generated for drivers (Format: `DRV-XXXYYY`)

### Booking & Payments
* Passengers can book seats on available trips
* Payments processed via M-Pesa Daraja API (STK Push)
* Payment confirmation stored & receipts issued

### Vehicles & Drivers
* Managers register vehicles with fleet number, license plate, capacity, GPS device ID, SIM number, GPS API key
* Managers assign drivers to vehicles
* System auto-links drivers and fleet numbers

### GPS Tracking
* Vehicles publish GPS data in real time (via API/Webhook)
* Users and managers view live vehicle locations on Mapbox
* Managers monitor trips in progress

### Admin & Manager Tools
* Managers can approve/reject trip logs
* Reports available in CSV (revenue, trips, drivers)
* Admin can configure fares, routes, system settings
* Admin has kill-switch to block vehicles/users

## Technical Requirements

* **Frontend**: React (PWA for passengers, Web dashboards for managers/admins)
* **Backend**: Python (FastAPI microservices)
* **Database**: Supabase PostgreSQL
* **Authentication**: Supabase Auth
* **GPS Integration**: 3rd-party GPS API
* **Payments**: M-Pesa Daraja API
* **Maps**: Mapbox
* **Infrastructure**: Docker for local dev, Render for deployment

## Success Criteria

* Real-time GPS tracking with minimal latency
* Secure payment processing with M-Pesa integration
* High availability for live tracking & booking
* Support for high concurrency (multiple trips & payments)
* Comprehensive reporting and analytics capabilities
