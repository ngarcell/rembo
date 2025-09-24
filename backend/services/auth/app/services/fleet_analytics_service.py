"""
Fleet performance analytics service
"""

import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from app.models.fleet_analytics import (
    PerformanceMetric,
    RoutePerformance,
    VehiclePerformanceSummary,
    FleetKPI,
)
from app.models.vehicle import Vehicle
from app.models.driver_profile import DriverProfile
from app.models.user_profile import UserProfile
from app.models.fleet import Fleet
from app.schemas.fleet_analytics import (
    MetricRecordRequest,
    RoutePerformanceRequest,
    KPIRequest,
    AnalyticsFilterRequest,
)


class FleetAnalyticsService:
    """Service for fleet performance analytics operations"""

    @staticmethod
    def record_performance_metric(
        fleet_id: str, request: MetricRecordRequest, manager_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Record a performance metric"""
        try:
            # Validate fleet access
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return False, {"error": "Fleet not found"}

            # Validate vehicle if provided
            if request.vehicle_id:
                vehicle = (
                    db.query(Vehicle)
                    .filter(
                        and_(
                            Vehicle.id == request.vehicle_id,
                            Vehicle.fleet_id == fleet_id,
                        )
                    )
                    .first()
                )
                if not vehicle:
                    return False, {"error": "Vehicle not found in this fleet"}

            # Validate driver if provided
            if request.driver_id:
                driver = (
                    db.query(DriverProfile)
                    .filter(
                        and_(
                            DriverProfile.id == request.driver_id,
                            DriverProfile.fleet_id == fleet_id,
                        )
                    )
                    .first()
                )
                if not driver:
                    return False, {"error": "Driver not found in this fleet"}

            # Create metric record
            metric = PerformanceMetric(
                vehicle_id=request.vehicle_id,
                fleet_id=fleet_id,
                metric_type=request.metric_type.value,
                metric_value=request.metric_value,
                metric_unit=request.metric_unit,
                date_recorded=request.date_recorded,
                period_start=request.period_start,
                period_end=request.period_end,
                route_id=request.route_id,
                driver_id=request.driver_id,
                notes=request.notes,
                recorded_by=manager_id,
            )

            db.add(metric)
            db.commit()
            db.refresh(metric)

            return True, {
                "message": "Performance metric recorded successfully",
                "metric_id": str(metric.id),
            }

        except SQLAlchemyError as e:
            db.rollback()
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            db.rollback()
            return False, {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def record_route_performance(
        fleet_id: str, request: RoutePerformanceRequest, manager_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Record route performance data"""
        try:
            # Validate fleet access
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return False, {"error": "Fleet not found"}

            # Calculate derived metrics
            fuel_efficiency = None
            if request.fuel_consumption_liters and request.fuel_consumption_liters > 0:
                fuel_efficiency = (
                    request.total_distance_km / request.fuel_consumption_liters
                )

            # Create route performance record
            route_perf = RoutePerformance(
                fleet_id=fleet_id,
                route_name=request.route_name,
                route_code=request.route_code,
                total_trips=request.total_trips,
                total_distance_km=request.total_distance_km,
                total_revenue=request.total_revenue,
                total_passengers=request.total_passengers,
                average_trip_time_minutes=request.average_trip_time_minutes,
                on_time_percentage=request.on_time_percentage,
                fuel_consumption_liters=request.fuel_consumption_liters,
                fuel_efficiency_km_per_liter=fuel_efficiency,
                maintenance_cost=request.maintenance_cost,
                date_recorded=request.period_start.date(),
                period_start=request.period_start,
                period_end=request.period_end,
                recorded_by=manager_id,
                notes=request.notes,
            )

            db.add(route_perf)
            db.commit()
            db.refresh(route_perf)

            return True, {
                "message": "Route performance recorded successfully",
                "route_performance_id": str(route_perf.id),
            }

        except SQLAlchemyError as e:
            db.rollback()
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            db.rollback()
            return False, {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def record_kpi(
        fleet_id: str, request: KPIRequest, manager_id: str, db: Session
    ) -> Tuple[bool, Dict[str, Any]]:
        """Record a KPI measurement"""
        try:
            # Validate fleet access
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return False, {"error": "Fleet not found"}

            # Calculate achievement percentage and trend
            achievement_percentage = None
            if request.target_value and request.target_value > 0:
                achievement_percentage = (
                    request.current_value / request.target_value
                ) * 100

            trend = None
            if request.previous_value is not None:
                if request.current_value > request.previous_value:
                    trend = "improving"
                elif request.current_value < request.previous_value:
                    trend = "declining"
                else:
                    trend = "stable"

            # Create KPI record
            kpi = FleetKPI(
                fleet_id=fleet_id,
                kpi_name=request.kpi_name,
                kpi_category=request.kpi_category,
                current_value=request.current_value,
                target_value=request.target_value,
                previous_value=request.previous_value,
                achievement_percentage=achievement_percentage,
                trend=trend,
                measurement_date=request.measurement_date,
                period_type=request.period_type.value,
                unit=request.unit,
                description=request.description,
                calculation_method=request.calculation_method,
                recorded_by=manager_id,
            )

            db.add(kpi)
            db.commit()
            db.refresh(kpi)

            return True, {
                "message": "KPI recorded successfully",
                "kpi_id": str(kpi.id),
                "achievement_percentage": achievement_percentage,
                "trend": trend,
            }

        except SQLAlchemyError as e:
            db.rollback()
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            db.rollback()
            return False, {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def get_fleet_metrics(
        fleet_id: str,
        filters: AnalyticsFilterRequest,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Dict[str, Any]:
        """Get performance metrics for a fleet"""
        try:
            # Base query
            query = db.query(PerformanceMetric).filter(
                PerformanceMetric.fleet_id == fleet_id
            )

            # Apply filters
            if filters.start_date:
                query = query.filter(
                    PerformanceMetric.date_recorded >= filters.start_date
                )
            if filters.end_date:
                query = query.filter(
                    PerformanceMetric.date_recorded <= filters.end_date
                )
            if filters.vehicle_ids:
                query = query.filter(
                    PerformanceMetric.vehicle_id.in_(filters.vehicle_ids)
                )
            if filters.driver_ids:
                query = query.filter(
                    PerformanceMetric.driver_id.in_(filters.driver_ids)
                )
            if filters.metric_types:
                metric_values = [mt.value for mt in filters.metric_types]
                query = query.filter(PerformanceMetric.metric_type.in_(metric_values))
            if filters.route_ids:
                query = query.filter(PerformanceMetric.route_id.in_(filters.route_ids))

            # Get total count
            total_count = query.count()

            # Apply pagination and ordering
            metrics = (
                query.order_by(desc(PerformanceMetric.date_recorded))
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            # Format response
            metrics_data = []
            for metric in metrics:
                # Get related data
                vehicle_info = None
                if metric.vehicle:
                    vehicle_info = f"{metric.vehicle.fleet_number} ({metric.vehicle.license_plate})"

                driver_name = None
                if metric.driver:
                    driver_name = f"{metric.driver.first_name or ''} {metric.driver.last_name or ''}".strip()

                recorder_name = "Unknown"
                if metric.recorder:
                    recorder_name = f"{metric.recorder.first_name or ''} {metric.recorder.last_name or ''}".strip()
                    if not recorder_name:
                        recorder_name = metric.recorder.phone

                metrics_data.append(
                    {
                        "id": str(metric.id),
                        "vehicle_id": (
                            str(metric.vehicle_id) if metric.vehicle_id else None
                        ),
                        "vehicle_info": vehicle_info,
                        "metric_type": metric.metric_type,
                        "metric_value": metric.metric_value,
                        "metric_unit": metric.metric_unit,
                        "date_recorded": metric.date_recorded,
                        "period_start": metric.period_start,
                        "period_end": metric.period_end,
                        "route_id": metric.route_id,
                        "driver_id": (
                            str(metric.driver_id) if metric.driver_id else None
                        ),
                        "driver_name": driver_name,
                        "notes": metric.notes,
                        "recorded_by": str(metric.recorded_by),
                        "recorder_name": recorder_name,
                        "created_at": metric.created_at,
                        "updated_at": metric.updated_at,
                    }
                )

            return {
                "metrics": metrics_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit,
            }

        except Exception as e:
            return {
                "error": f"Error retrieving metrics: {str(e)}",
                "metrics": [],
                "total_count": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
            }

    @staticmethod
    def get_route_performance(
        fleet_id: str,
        filters: AnalyticsFilterRequest,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Dict[str, Any]:
        """Get route performance data for a fleet"""
        try:
            # Base query
            query = db.query(RoutePerformance).filter(
                RoutePerformance.fleet_id == fleet_id
            )

            # Apply filters
            if filters.start_date:
                query = query.filter(
                    RoutePerformance.date_recorded >= filters.start_date
                )
            if filters.end_date:
                query = query.filter(RoutePerformance.date_recorded <= filters.end_date)
            if filters.route_ids:
                query = query.filter(RoutePerformance.route_code.in_(filters.route_ids))

            # Get total count
            total_count = query.count()

            # Apply pagination and ordering
            route_performances = (
                query.order_by(desc(RoutePerformance.date_recorded))
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            # Format response
            route_data = []
            for rp in route_performances:
                recorder_name = "Unknown"
                if rp.recorder:
                    recorder_name = f"{rp.recorder.first_name or ''} {rp.recorder.last_name or ''}".strip()
                    if not recorder_name:
                        recorder_name = rp.recorder.phone

                route_data.append(
                    {
                        "id": str(rp.id),
                        "route_name": rp.route_name,
                        "route_code": rp.route_code,
                        "total_trips": rp.total_trips,
                        "total_distance_km": rp.total_distance_km,
                        "total_revenue": rp.total_revenue,
                        "total_passengers": rp.total_passengers,
                        "average_trip_time_minutes": rp.average_trip_time_minutes,
                        "on_time_percentage": rp.on_time_percentage,
                        "fuel_consumption_liters": rp.fuel_consumption_liters,
                        "fuel_efficiency_km_per_liter": rp.fuel_efficiency_km_per_liter,
                        "maintenance_cost": rp.maintenance_cost,
                        "date_recorded": rp.date_recorded,
                        "period_start": rp.period_start,
                        "period_end": rp.period_end,
                        "recorded_by": str(rp.recorded_by),
                        "recorder_name": recorder_name,
                        "notes": rp.notes,
                        "created_at": rp.created_at,
                        "updated_at": rp.updated_at,
                    }
                )

            return {
                "route_performance": route_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit,
            }

        except Exception as e:
            return {
                "error": f"Error retrieving route performance: {str(e)}",
                "route_performance": [],
                "total_count": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
            }

    @staticmethod
    def get_fleet_kpis(
        fleet_id: str,
        filters: AnalyticsFilterRequest,
        page: int = 1,
        limit: int = 20,
        db: Session = None,
    ) -> Dict[str, Any]:
        """Get KPIs for a fleet"""
        try:
            # Base query
            query = db.query(FleetKPI).filter(FleetKPI.fleet_id == fleet_id)

            # Apply filters
            if filters.start_date:
                query = query.filter(FleetKPI.measurement_date >= filters.start_date)
            if filters.end_date:
                query = query.filter(FleetKPI.measurement_date <= filters.end_date)
            if filters.period_type:
                query = query.filter(FleetKPI.period_type == filters.period_type.value)

            # Get total count
            total_count = query.count()

            # Apply pagination and ordering
            kpis = (
                query.order_by(desc(FleetKPI.measurement_date))
                .offset((page - 1) * limit)
                .limit(limit)
                .all()
            )

            # Format response
            kpi_data = []
            for kpi in kpis:
                recorder_name = "Unknown"
                if kpi.recorder:
                    recorder_name = f"{kpi.recorder.first_name or ''} {kpi.recorder.last_name or ''}".strip()
                    if not recorder_name:
                        recorder_name = kpi.recorder.phone

                kpi_data.append(
                    {
                        "id": str(kpi.id),
                        "kpi_name": kpi.kpi_name,
                        "kpi_category": kpi.kpi_category,
                        "current_value": kpi.current_value,
                        "target_value": kpi.target_value,
                        "previous_value": kpi.previous_value,
                        "achievement_percentage": kpi.achievement_percentage,
                        "trend": kpi.trend,
                        "measurement_date": kpi.measurement_date,
                        "period_type": kpi.period_type,
                        "unit": kpi.unit,
                        "description": kpi.description,
                        "calculation_method": kpi.calculation_method,
                        "recorded_by": str(kpi.recorded_by),
                        "recorder_name": recorder_name,
                        "created_at": kpi.created_at,
                        "updated_at": kpi.updated_at,
                    }
                )

            return {
                "kpis": kpi_data,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit,
            }

        except Exception as e:
            return {
                "error": f"Error retrieving KPIs: {str(e)}",
                "kpis": [],
                "total_count": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
            }

    @staticmethod
    def get_fleet_dashboard(
        fleet_id: str, target_date: Optional[date] = None, db: Session = None
    ) -> Dict[str, Any]:
        """Get fleet dashboard summary"""
        try:
            if not target_date:
                target_date = date.today()

            # Get fleet info
            fleet = db.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                return {"error": "Fleet not found"}

            # Fleet overview
            total_vehicles = (
                db.query(Vehicle).filter(Vehicle.fleet_id == fleet_id).count()
            )
            active_vehicles = (
                db.query(Vehicle)
                .filter(and_(Vehicle.fleet_id == fleet_id, Vehicle.status == "active"))
                .count()
            )

            total_drivers = (
                db.query(DriverProfile)
                .filter(DriverProfile.fleet_id == fleet_id)
                .count()
            )
            active_drivers = (
                db.query(DriverProfile)
                .filter(
                    and_(
                        DriverProfile.fleet_id == fleet_id,
                        DriverProfile.employment_status == "active",
                    )
                )
                .count()
            )

            # Today's performance metrics
            today_metrics = (
                db.query(PerformanceMetric)
                .filter(
                    and_(
                        PerformanceMetric.fleet_id == fleet_id,
                        PerformanceMetric.date_recorded == target_date,
                    )
                )
                .all()
            )

            total_trips_today = 0
            total_revenue_today = 0
            total_passengers_today = 0
            total_distance_today = 0.0

            for metric in today_metrics:
                if metric.metric_type == "trip_count":
                    total_trips_today += int(metric.metric_value)
                elif metric.metric_type == "revenue":
                    total_revenue_today += int(metric.metric_value)
                elif metric.metric_type == "passenger_count":
                    total_passengers_today += int(metric.metric_value)
                elif metric.metric_type == "distance_traveled":
                    total_distance_today += metric.metric_value

            # Calculate efficiency metrics
            fleet_utilization_rate = None
            if total_vehicles > 0:
                fleet_utilization_rate = (active_vehicles / total_vehicles) * 100

            # Get average fuel efficiency
            fuel_efficiency_metrics = (
                db.query(PerformanceMetric)
                .filter(
                    and_(
                        PerformanceMetric.fleet_id == fleet_id,
                        PerformanceMetric.metric_type == "fuel_efficiency",
                        PerformanceMetric.date_recorded
                        >= target_date - timedelta(days=7),
                    )
                )
                .all()
            )

            average_fuel_efficiency = None
            if fuel_efficiency_metrics:
                total_efficiency = sum(m.metric_value for m in fuel_efficiency_metrics)
                average_fuel_efficiency = total_efficiency / len(
                    fuel_efficiency_metrics
                )

            # Get on-time performance
            on_time_metrics = (
                db.query(PerformanceMetric)
                .filter(
                    and_(
                        PerformanceMetric.fleet_id == fleet_id,
                        PerformanceMetric.metric_type == "on_time_performance",
                        PerformanceMetric.date_recorded
                        >= target_date - timedelta(days=7),
                    )
                )
                .all()
            )

            on_time_performance = None
            if on_time_metrics:
                total_on_time = sum(m.metric_value for m in on_time_metrics)
                on_time_performance = total_on_time / len(on_time_metrics)

            # Financial metrics (simplified)
            total_operating_cost = 0
            net_profit_today = total_revenue_today - total_operating_cost
            profit_margin = None
            if total_revenue_today > 0:
                profit_margin = (net_profit_today / total_revenue_today) * 100

            # Top performing vehicles (mock data for now)
            top_performing_vehicles = [
                {
                    "vehicle_id": "sample",
                    "fleet_number": "KCS-001",
                    "trips": 12,
                    "revenue": 15000,
                },
                {
                    "vehicle_id": "sample",
                    "fleet_number": "KCS-002",
                    "trips": 10,
                    "revenue": 12000,
                },
            ]

            # Top performing routes (mock data for now)
            top_performing_routes = [
                {"route_name": "Nairobi-Nakuru", "trips": 25, "revenue": 50000},
                {"route_name": "Nairobi-Mombasa", "trips": 15, "revenue": 75000},
            ]

            # Maintenance alerts (simplified)
            vehicles_needing_maintenance = (
                db.query(Vehicle)
                .filter(
                    and_(Vehicle.fleet_id == fleet_id, Vehicle.status == "maintenance")
                )
                .count()
            )

            return {
                "fleet_id": str(fleet_id),
                "fleet_name": fleet.name,
                "summary_date": target_date,
                "total_vehicles": total_vehicles,
                "active_vehicles": active_vehicles,
                "total_drivers": total_drivers,
                "active_drivers": active_drivers,
                "total_trips_today": total_trips_today,
                "total_revenue_today": total_revenue_today,
                "total_passengers_today": total_passengers_today,
                "total_distance_today": total_distance_today,
                "fleet_utilization_rate": fleet_utilization_rate,
                "average_fuel_efficiency": average_fuel_efficiency,
                "on_time_performance": on_time_performance,
                "total_operating_cost": total_operating_cost,
                "net_profit_today": net_profit_today,
                "profit_margin": profit_margin,
                "top_performing_vehicles": top_performing_vehicles,
                "top_performing_routes": top_performing_routes,
                "vehicles_needing_maintenance": vehicles_needing_maintenance,
                "overdue_maintenance": 0,
                "fuel_efficiency_alerts": 0,
            }

        except Exception as e:
            return {"error": f"Error generating dashboard: {str(e)}"}
