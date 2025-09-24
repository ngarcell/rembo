"""
Fleet performance analytics endpoints
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.middleware.auth_middleware import require_manager
from app.models.user_profile import UserProfile
from app.services.fleet_analytics_service import FleetAnalyticsService
from app.schemas.fleet_analytics import (
    MetricRecordRequest,
    RoutePerformanceRequest,
    KPIRequest,
    AnalyticsFilterRequest,
    MetricResponse,
    RoutePerformanceResponse,
    KPIResponse,
    FleetDashboardResponse,
    AnalyticsListResponse,
    MetricTypeEnum,
    PeriodTypeEnum,
)

router = APIRouter()


@router.post("/metrics")
def record_performance_metric(
    request: MetricRecordRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Record a performance metric for the fleet"""
    success, result = FleetAnalyticsService.record_performance_metric(
        fleet_id=str(manager.fleet_id),
        request=request,
        manager_id=str(manager.id),
        db=db,
    )

    if not success:
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to record metric")
        )

    return {
        "success": True,
        "message": result["message"],
        "metric_id": result["metric_id"],
    }


@router.get("/metrics")
def get_fleet_metrics(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    vehicle_ids: Optional[str] = Query(None, description="Comma-separated vehicle IDs"),
    driver_ids: Optional[str] = Query(None, description="Comma-separated driver IDs"),
    route_ids: Optional[str] = Query(None, description="Comma-separated route IDs"),
    metric_types: Optional[str] = Query(
        None, description="Comma-separated metric types"
    ),
    period_type: Optional[PeriodTypeEnum] = Query(
        None, description="Period type for aggregation"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get performance metrics for the fleet"""

    # Parse comma-separated parameters
    vehicle_id_list = vehicle_ids.split(",") if vehicle_ids else None
    driver_id_list = driver_ids.split(",") if driver_ids else None
    route_id_list = route_ids.split(",") if route_ids else None

    metric_type_list = None
    if metric_types:
        try:
            metric_type_list = [
                MetricTypeEnum(mt.strip()) for mt in metric_types.split(",")
            ]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid metric type: {str(e)}"
            )

    # Create filter request
    filters = AnalyticsFilterRequest(
        start_date=start_date,
        end_date=end_date,
        vehicle_ids=vehicle_id_list,
        driver_ids=driver_id_list,
        route_ids=route_id_list,
        metric_types=metric_type_list,
        period_type=period_type,
    )

    result = FleetAnalyticsService.get_fleet_metrics(
        fleet_id=str(manager.fleet_id), filters=filters, page=page, limit=limit, db=db
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/routes/performance")
def record_route_performance(
    request: RoutePerformanceRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Record route performance data"""
    success, result = FleetAnalyticsService.record_route_performance(
        fleet_id=str(manager.fleet_id),
        request=request,
        manager_id=str(manager.id),
        db=db,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to record route performance"),
        )

    return {
        "success": True,
        "message": result["message"],
        "route_performance_id": result["route_performance_id"],
    }


@router.get("/routes/performance")
def get_route_performance(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    route_ids: Optional[str] = Query(None, description="Comma-separated route IDs"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get route performance data for the fleet"""

    # Parse comma-separated parameters
    route_id_list = route_ids.split(",") if route_ids else None

    # Create filter request
    filters = AnalyticsFilterRequest(
        start_date=start_date, end_date=end_date, route_ids=route_id_list
    )

    result = FleetAnalyticsService.get_route_performance(
        fleet_id=str(manager.fleet_id), filters=filters, page=page, limit=limit, db=db
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/kpis")
def record_kpi(
    request: KPIRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Record a KPI measurement"""
    success, result = FleetAnalyticsService.record_kpi(
        fleet_id=str(manager.fleet_id),
        request=request,
        manager_id=str(manager.id),
        db=db,
    )

    if not success:
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to record KPI")
        )

    return {
        "success": True,
        "message": result["message"],
        "kpi_id": result["kpi_id"],
        "achievement_percentage": result.get("achievement_percentage"),
        "trend": result.get("trend"),
    }


@router.get("/kpis")
def get_fleet_kpis(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    period_type: Optional[PeriodTypeEnum] = Query(
        None, description="Period type filter"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get KPIs for the fleet"""

    # Create filter request
    filters = AnalyticsFilterRequest(
        start_date=start_date, end_date=end_date, period_type=period_type
    )

    result = FleetAnalyticsService.get_fleet_kpis(
        fleet_id=str(manager.fleet_id), filters=filters, page=page, limit=limit, db=db
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/dashboard")
def get_fleet_dashboard(
    target_date: Optional[date] = Query(
        None, description="Target date for dashboard (defaults to today)"
    ),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get fleet dashboard summary"""

    result = FleetAnalyticsService.get_fleet_dashboard(
        fleet_id=str(manager.fleet_id), target_date=target_date, db=db
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/summary")
def get_analytics_summary(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """Get comprehensive analytics summary"""

    # Create basic filters
    filters = AnalyticsFilterRequest(start_date=start_date, end_date=end_date)

    # Get all analytics data
    metrics_result = FleetAnalyticsService.get_fleet_metrics(
        fleet_id=str(manager.fleet_id), filters=filters, page=1, limit=10, db=db
    )

    routes_result = FleetAnalyticsService.get_route_performance(
        fleet_id=str(manager.fleet_id), filters=filters, page=1, limit=10, db=db
    )

    kpis_result = FleetAnalyticsService.get_fleet_kpis(
        fleet_id=str(manager.fleet_id), filters=filters, page=1, limit=10, db=db
    )

    return {
        "metrics": metrics_result.get("metrics", []),
        "route_performance": routes_result.get("route_performance", []),
        "kpis": kpis_result.get("kpis", []),
        "summary_period": {"start_date": start_date, "end_date": end_date},
    }
