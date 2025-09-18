# System Overview

## Architecture Principles

* **Microservices Architecture**: Decomposed into focused, independently deployable services
* **Event-Driven Design**: Asynchronous communication between services using events
* **API-First Approach**: All services expose well-defined REST APIs
* **Real-time Capabilities**: WebSocket connections for live GPS tracking and notifications
* **Security by Design**: Authentication, authorization, and data encryption at every layer
* **Scalability**: Horizontal scaling capabilities for high-traffic scenarios
* **Observability**: Comprehensive logging, monitoring, and tracing

## High-Level Architecture

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
