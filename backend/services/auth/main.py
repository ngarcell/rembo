"""
Auth Service - Main FastAPI Application
Handles user authentication, registration, and authorization
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base, init_db, get_db
from app.api.v1.api import api_router
from app.core.redis_client import redis_client
from app.core.supabase_client import supabase_client
from app.services.admin_service import AdminService
from app.services.jwt_service import jwt_service

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Auth Service starting up...")

    # Create database tables
    init_db()

    # Create default fleets
    try:
        db = next(get_db())
        AdminService.create_default_fleets(db)
        db.close()
    except Exception as e:
        print(f"⚠️ Failed to create default fleets: {e}")

    # Test Redis connection
    try:
        redis_client.ping()
        print("✅ Redis connection established")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

    # Test Supabase connection
    try:
        if supabase_client.test_connection():
            print("✅ Supabase connection established")
        else:
            print("⚠️ Supabase connection not configured or failed")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")

    print("✅ Auth Service startup complete")

    yield

    # Shutdown
    print("🛑 Auth Service shutting down...")
    redis_client.close()
    print("✅ Auth Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Matatu Fleet Auth Service",
    description="Authentication and authorization service for Matatu Fleet Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "service": "Matatu Fleet Auth Service",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "supabase": "unknown",
    }

    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        # Test Redis connection
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        # Test Supabase connection
        if supabase_client.test_connection():
            health_status["supabase"] = "connected"
        else:
            health_status["supabase"] = "not configured"
    except Exception as e:
        health_status["supabase"] = f"error: {str(e)}"

    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status


@app.post("/debug/create-manager-token")
def create_manager_token():
    """Create a JWT token for testing manager functionality"""
    # Use the Samuel Rembo Manager for testing
    user_id = "b31f64ae-f16b-45ad-882a-446611533916"
    phone = "+254700777666"
    role = "manager"

    access_token = jwt_service.create_access_token(
        user_id=user_id, phone=phone, role=role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "phone": phone,
        "role": role,
    }


@app.post("/debug/create-test-data")
def create_test_data():
    """Create test data for development"""
    from app.models.trip import Route, Trip
    from app.models.simple_vehicle import SimpleVehicle
    from app.models.fleet import Fleet
    from app.models.simple_driver import SimpleDriver
    from datetime import datetime, timezone, timedelta
    import uuid

    db = next(get_db())
    try:
        # Get the first available fleet or create one
        fleet = db.query(Fleet).first()
        if not fleet:
            fleet = Fleet(
                id=uuid.uuid4(),
                name="Test Fleet",
                description="Test fleet for development",
                is_active=True
            )
            db.add(fleet)
            db.flush()  # Get the ID

        # Create a test route
        route = Route(
            id=uuid.uuid4(),
            name="Nairobi - Kisumu Express",
            origin="Nairobi",
            destination="Kisumu",
            distance_km=350.0,
            estimated_duration_minutes=420,
            base_fare=1500.00,
            is_active=True
        )
        db.add(route)
        db.flush()  # Get the ID

        # Create a test driver
        driver = SimpleDriver(
            id=uuid.uuid4(),
            driver_code="DRV-001",
            license_number="DL123456789",
            fleet_id=fleet.id,
            is_active=True
        )
        db.add(driver)
        db.flush()  # Get the ID

        # Create a test vehicle
        vehicle = SimpleVehicle(
            id=uuid.uuid4(),
            fleet_id=fleet.id,
            fleet_number="KCS-001",
            license_plate="KCA123A",
            capacity=14,
            vehicle_model="Toyota Hiace",
            status="active"
        )
        db.add(vehicle)
        db.flush()  # Get the ID

        # Create a test trip
        departure_time = datetime.now(timezone.utc) + timedelta(hours=2)
        arrival_time = departure_time + timedelta(hours=7)

        trip = Trip(
            id=uuid.uuid4(),
            route_id=route.id,
            vehicle_id=vehicle.id,
            driver_id=driver.id,
            scheduled_departure=departure_time,
            scheduled_arrival=arrival_time,
            fare=1500.00,
            total_seats=14,
            available_seats=14,
            status="scheduled"
        )
        db.add(trip)

        db.commit()

        return {
            "success": True,
            "message": "Test data created successfully",
            "fleet_id": str(fleet.id),
            "driver_id": str(driver.id),
            "route_id": str(route.id),
            "vehicle_id": str(vehicle.id),
            "trip_id": str(trip.id)
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
    )
