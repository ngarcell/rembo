"""
Fleet performance analytics models
"""

import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    Date,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class MetricTypeEnum(str, Enum):
    """Types of performance metrics"""

    FUEL_EFFICIENCY = "fuel_efficiency"
    REVENUE = "revenue"
    PASSENGER_COUNT = "passenger_count"
    TRIP_COUNT = "trip_count"
    DISTANCE_TRAVELED = "distance_traveled"
    MAINTENANCE_COST = "maintenance_cost"
    DOWNTIME = "downtime"
    UTILIZATION_RATE = "utilization_rate"
    AVERAGE_SPEED = "average_speed"
    ON_TIME_PERFORMANCE = "on_time_performance"


class PerformanceMetric(Base):
    """Store performance metrics for vehicles and fleet"""

    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=True,  # Null for fleet-wide metrics
        index=True,
    )
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_type = Column(String(50), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # km, liters, KES, hours, etc.

    # Time period
    date_recorded = Column(Date, nullable=False, index=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Context
    route_id = Column(String(100), nullable=True, index=True)
    driver_id = Column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True
    )

    # Additional data
    notes = Column(Text, nullable=True)
    recorded_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    fleet = relationship("Fleet")
    driver = relationship("SimpleDriver")
    recorder = relationship("UserProfile")


class RoutePerformance(Base):
    """Track performance metrics by route"""

    __tablename__ = "route_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    route_name = Column(String(200), nullable=False, index=True)
    route_code = Column(String(50), nullable=True, index=True)

    # Performance metrics
    total_trips = Column(Integer, default=0, nullable=False)
    total_distance_km = Column(Float, default=0.0, nullable=False)
    total_revenue = Column(Integer, default=0, nullable=False)  # In cents
    total_passengers = Column(Integer, default=0, nullable=False)
    average_trip_time_minutes = Column(Float, nullable=True)
    on_time_percentage = Column(Float, nullable=True)

    # Efficiency metrics
    fuel_consumption_liters = Column(Float, nullable=True)
    fuel_efficiency_km_per_liter = Column(Float, nullable=True)
    maintenance_cost = Column(Integer, default=0, nullable=False)  # In cents

    # Time period
    date_recorded = Column(Date, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Metadata
    recorded_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    fleet = relationship("Fleet")
    recorder = relationship("UserProfile")


class VehiclePerformanceSummary(Base):
    """Daily/weekly/monthly performance summary for vehicles"""

    __tablename__ = "vehicle_performance_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Summary period
    summary_date = Column(Date, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly

    # Operational metrics
    trips_completed = Column(Integer, default=0, nullable=False)
    total_distance_km = Column(Float, default=0.0, nullable=False)
    total_revenue = Column(Integer, default=0, nullable=False)  # In cents
    total_passengers = Column(Integer, default=0, nullable=False)
    active_hours = Column(Float, default=0.0, nullable=False)

    # Efficiency metrics
    fuel_consumed_liters = Column(Float, nullable=True)
    fuel_cost = Column(Integer, nullable=True)  # In cents
    maintenance_cost = Column(Integer, default=0, nullable=False)  # In cents
    utilization_rate = Column(Float, nullable=True)  # Percentage

    # Performance indicators
    average_speed_kmh = Column(Float, nullable=True)
    on_time_trips = Column(Integer, default=0, nullable=False)
    delayed_trips = Column(Integer, default=0, nullable=False)
    cancelled_trips = Column(Integer, default=0, nullable=False)

    # Financial metrics
    gross_revenue = Column(Integer, default=0, nullable=False)  # In cents
    operating_cost = Column(Integer, default=0, nullable=False)  # In cents
    net_profit = Column(Integer, default=0, nullable=False)  # In cents
    profit_margin = Column(Float, nullable=True)  # Percentage

    # Driver assignment
    primary_driver_id = Column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    vehicle = relationship("SimpleVehicle")
    fleet = relationship("Fleet")
    primary_driver = relationship("SimpleDriver")


class FleetKPI(Base):
    """Key Performance Indicators for fleet management"""

    __tablename__ = "fleet_kpis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fleet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # KPI identification
    kpi_name = Column(String(100), nullable=False, index=True)
    kpi_category = Column(
        String(50), nullable=False, index=True
    )  # operational, financial, safety, etc.

    # Values
    current_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=True)
    previous_value = Column(Float, nullable=True)

    # Performance
    achievement_percentage = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True)  # improving, declining, stable

    # Time period
    measurement_date = Column(Date, nullable=False, index=True)
    period_type = Column(
        String(20), nullable=False
    )  # daily, weekly, monthly, quarterly

    # Metadata
    unit = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    calculation_method = Column(Text, nullable=True)

    recorded_by = Column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    fleet = relationship("Fleet")
    recorder = relationship("UserProfile")
