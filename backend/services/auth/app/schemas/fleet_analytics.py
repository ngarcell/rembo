"""
Fleet performance analytics schemas
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


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


class PeriodTypeEnum(str, Enum):
    """Time period types for analytics"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendEnum(str, Enum):
    """Performance trend indicators"""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


# Request Schemas
class MetricRecordRequest(BaseModel):
    """Request to record a performance metric"""

    vehicle_id: Optional[str] = Field(
        None, description="Vehicle ID (null for fleet-wide metrics)"
    )
    metric_type: MetricTypeEnum = Field(
        ..., description="Type of metric being recorded"
    )
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Unit of measurement")
    date_recorded: date = Field(..., description="Date when metric was recorded")
    period_start: Optional[datetime] = Field(
        None, description="Start of measurement period"
    )
    period_end: Optional[datetime] = Field(
        None, description="End of measurement period"
    )
    route_id: Optional[str] = Field(None, description="Route identifier")
    driver_id: Optional[str] = Field(None, description="Driver ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class RoutePerformanceRequest(BaseModel):
    """Request to record route performance data"""

    route_name: str = Field(..., max_length=200, description="Route name")
    route_code: Optional[str] = Field(None, max_length=50, description="Route code")
    total_trips: int = Field(0, ge=0, description="Total trips completed")
    total_distance_km: float = Field(
        0.0, ge=0, description="Total distance in kilometers"
    )
    total_revenue: int = Field(0, ge=0, description="Total revenue in cents")
    total_passengers: int = Field(0, ge=0, description="Total passengers carried")
    average_trip_time_minutes: Optional[float] = Field(
        None, ge=0, description="Average trip time"
    )
    on_time_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="On-time performance percentage"
    )
    fuel_consumption_liters: Optional[float] = Field(
        None, ge=0, description="Fuel consumed in liters"
    )
    fuel_efficiency_km_per_liter: Optional[float] = Field(
        None, ge=0, description="Fuel efficiency"
    )
    maintenance_cost: int = Field(0, ge=0, description="Maintenance cost in cents")
    period_start: datetime = Field(..., description="Period start time")
    period_end: datetime = Field(..., description="Period end time")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class KPIRequest(BaseModel):
    """Request to record a KPI"""

    kpi_name: str = Field(..., max_length=100, description="KPI name")
    kpi_category: str = Field(..., max_length=50, description="KPI category")
    current_value: float = Field(..., description="Current KPI value")
    target_value: Optional[float] = Field(None, description="Target KPI value")
    previous_value: Optional[float] = Field(None, description="Previous KPI value")
    measurement_date: date = Field(..., description="Measurement date")
    period_type: PeriodTypeEnum = Field(..., description="Period type")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of measurement")
    description: Optional[str] = Field(
        None, max_length=500, description="KPI description"
    )
    calculation_method: Optional[str] = Field(
        None, max_length=1000, description="How KPI is calculated"
    )


class AnalyticsFilterRequest(BaseModel):
    """Request filters for analytics queries"""

    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")
    vehicle_ids: Optional[List[str]] = Field(
        None, description="Filter by specific vehicles"
    )
    route_ids: Optional[List[str]] = Field(
        None, description="Filter by specific routes"
    )
    driver_ids: Optional[List[str]] = Field(
        None, description="Filter by specific drivers"
    )
    metric_types: Optional[List[MetricTypeEnum]] = Field(
        None, description="Filter by metric types"
    )
    period_type: Optional[PeriodTypeEnum] = Field(
        None, description="Period type for aggregation"
    )


# Response Schemas
class MetricResponse(BaseModel):
    """Performance metric response"""

    id: str
    vehicle_id: Optional[str]
    vehicle_info: Optional[str]
    metric_type: str
    metric_value: float
    metric_unit: Optional[str]
    date_recorded: date
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    route_id: Optional[str]
    driver_id: Optional[str]
    driver_name: Optional[str]
    notes: Optional[str]
    recorded_by: str
    recorder_name: str
    created_at: datetime
    updated_at: datetime


class RoutePerformanceResponse(BaseModel):
    """Route performance response"""

    id: str
    route_name: str
    route_code: Optional[str]
    total_trips: int
    total_distance_km: float
    total_revenue: int
    total_passengers: int
    average_trip_time_minutes: Optional[float]
    on_time_percentage: Optional[float]
    fuel_consumption_liters: Optional[float]
    fuel_efficiency_km_per_liter: Optional[float]
    maintenance_cost: int
    date_recorded: date
    period_start: datetime
    period_end: datetime
    recorded_by: str
    recorder_name: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VehiclePerformanceSummaryResponse(BaseModel):
    """Vehicle performance summary response"""

    id: str
    vehicle_id: str
    vehicle_info: str
    summary_date: date
    period_type: str
    trips_completed: int
    total_distance_km: float
    total_revenue: int
    total_passengers: int
    active_hours: float
    fuel_consumed_liters: Optional[float]
    fuel_cost: Optional[int]
    maintenance_cost: int
    utilization_rate: Optional[float]
    average_speed_kmh: Optional[float]
    on_time_trips: int
    delayed_trips: int
    cancelled_trips: int
    gross_revenue: int
    operating_cost: int
    net_profit: int
    profit_margin: Optional[float]
    primary_driver_id: Optional[str]
    primary_driver_name: Optional[str]
    created_at: datetime
    updated_at: datetime


class KPIResponse(BaseModel):
    """KPI response"""

    id: str
    kpi_name: str
    kpi_category: str
    current_value: float
    target_value: Optional[float]
    previous_value: Optional[float]
    achievement_percentage: Optional[float]
    trend: Optional[str]
    measurement_date: date
    period_type: str
    unit: Optional[str]
    description: Optional[str]
    calculation_method: Optional[str]
    recorded_by: str
    recorder_name: str
    created_at: datetime
    updated_at: datetime


class FleetDashboardResponse(BaseModel):
    """Fleet dashboard summary response"""

    fleet_id: str
    fleet_name: str
    summary_date: date

    # Fleet overview
    total_vehicles: int
    active_vehicles: int
    total_drivers: int
    active_drivers: int

    # Performance metrics
    total_trips_today: int
    total_revenue_today: int
    total_passengers_today: int
    total_distance_today: float

    # Efficiency metrics
    fleet_utilization_rate: Optional[float]
    average_fuel_efficiency: Optional[float]
    on_time_performance: Optional[float]

    # Financial metrics
    total_operating_cost: int
    net_profit_today: int
    profit_margin: Optional[float]

    # Top performers
    top_performing_vehicles: List[Dict[str, Any]]
    top_performing_routes: List[Dict[str, Any]]

    # Alerts and issues
    vehicles_needing_maintenance: int
    overdue_maintenance: int
    fuel_efficiency_alerts: int


class AnalyticsListResponse(BaseModel):
    """Paginated analytics list response"""

    metrics: List[MetricResponse] = []
    route_performance: List[RoutePerformanceResponse] = []
    vehicle_summaries: List[VehiclePerformanceSummaryResponse] = []
    kpis: List[KPIResponse] = []
    total_count: int
    page: int
    limit: int
    total_pages: int
