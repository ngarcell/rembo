# Story 2.4: Fleet Performance Analytics

**Epic**: Epic 2 - Fleet & Vehicle Management  
**Story ID**: 2.4  
**Priority**: P2 (Medium)  
**Estimated Effort**: 6 Story Points  
**Status**: 🔄 NOT_STARTED

## 📋 Story Description

**As a manager, I want to view fleet performance analytics and reports so that I can make data-driven decisions to optimize operations, reduce costs, and improve service quality.**

## 🎯 Acceptance Criteria

### ✅ **Performance Metrics**
- [ ] Vehicle utilization rates (active time vs. idle time)
- [ ] Driver performance metrics (trips completed, ratings, incidents)
- [ ] Route efficiency analysis (time, fuel consumption, passenger load)
- [ ] Revenue per vehicle and per driver
- [ ] Maintenance cost analysis per vehicle

### ✅ **Reporting Dashboard**
- [ ] Real-time fleet overview with key metrics
- [ ] Historical performance trends (daily, weekly, monthly)
- [ ] Comparative analysis between vehicles and drivers
- [ ] Cost analysis and profitability reports
- [ ] Customizable date ranges for all reports

### ✅ **Data Visualization**
- [ ] Interactive charts and graphs
- [ ] Performance trend lines
- [ ] Heat maps for route popularity
- [ ] Pie charts for cost breakdowns
- [ ] Export functionality (PDF, Excel)

## 🔧 Technical Requirements

### **Database Schema**
```sql
-- Performance metrics aggregation table
CREATE TABLE fleet_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    metric_date DATE NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES driver_profiles(id),
    
    -- Operational metrics
    trips_completed INTEGER DEFAULT 0,
    total_distance_km DECIMAL(10,2) DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    total_passengers INTEGER DEFAULT 0,
    active_hours DECIMAL(5,2) DEFAULT 0,
    idle_hours DECIMAL(5,2) DEFAULT 0,
    
    -- Cost metrics
    fuel_cost DECIMAL(10,2) DEFAULT 0,
    maintenance_cost DECIMAL(10,2) DEFAULT 0,
    other_costs DECIMAL(10,2) DEFAULT 0,
    
    -- Performance indicators
    utilization_rate DECIMAL(5,2), -- percentage
    revenue_per_km DECIMAL(8,2),
    passengers_per_trip DECIMAL(4,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(fleet_id, metric_date, vehicle_id, driver_id)
);

-- Route performance tracking
CREATE TABLE route_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_name VARCHAR(255) NOT NULL,
    fleet_id UUID NOT NULL REFERENCES fleets(id),
    metric_date DATE NOT NULL,
    
    total_trips INTEGER DEFAULT 0,
    total_passengers INTEGER DEFAULT 0,
    average_trip_time DECIMAL(5,2), -- in hours
    total_revenue DECIMAL(12,2) DEFAULT 0,
    popularity_score DECIMAL(5,2), -- calculated metric
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(route_name, fleet_id, metric_date)
);

-- Create indexes for performance
CREATE INDEX idx_performance_metrics_fleet_date ON fleet_performance_metrics(fleet_id, metric_date);
CREATE INDEX idx_performance_metrics_vehicle ON fleet_performance_metrics(vehicle_id, metric_date);
CREATE INDEX idx_route_performance_fleet_date ON route_performance(fleet_id, metric_date);
```

### **API Endpoints**
- `GET /api/v1/manager/analytics/dashboard` - Fleet performance dashboard
- `GET /api/v1/manager/analytics/vehicles` - Vehicle performance comparison
- `GET /api/v1/manager/analytics/drivers` - Driver performance metrics
- `GET /api/v1/manager/analytics/routes` - Route performance analysis
- `GET /api/v1/manager/analytics/costs` - Cost analysis and breakdown
- `GET /api/v1/manager/analytics/trends` - Historical trend analysis
- `GET /api/v1/manager/analytics/export` - Export reports (PDF/Excel)

### **Pydantic Models**
```python
class FleetDashboard(BaseModel):
    total_vehicles: int
    active_vehicles: int
    total_drivers: int
    active_drivers: int
    today_trips: int
    today_revenue: Decimal
    fleet_utilization: Decimal
    top_performing_vehicle: Optional[str]
    top_performing_driver: Optional[str]

class VehiclePerformance(BaseModel):
    vehicle_id: str
    fleet_number: str
    license_plate: str
    utilization_rate: Decimal
    total_trips: int
    total_revenue: Decimal
    maintenance_cost: Decimal
    profit_margin: Decimal

class PerformanceTrend(BaseModel):
    date: str
    trips: int
    revenue: Decimal
    utilization: Decimal
    costs: Decimal
```

## 🧪 Testing Strategy

### **Unit Tests**
- Metrics calculation algorithms
- Data aggregation functions
- Report generation logic
- Export functionality
- Performance trend analysis

### **Integration Tests**
- Dashboard data accuracy
- Real-time metrics updates
- Report export workflows
- Historical data analysis
- Cross-metric correlations

## 📊 Definition of Done

- [ ] Analytics dashboard implemented
- [ ] Performance metrics calculated correctly
- [ ] Historical trend analysis working
- [ ] Export functionality operational
- [ ] Data visualization components ready
- [ ] All tests passing
- [ ] API documentation complete
- [ ] Frontend analytics interface updated

## 🔗 Dependencies

- **Prerequisite**: Story 2.1 (Vehicle Registration) ✅ COMPLETED
- **Prerequisite**: Story 2.2 (Driver-Vehicle Assignment)
- **Future**: Epic 3 (Trip data for comprehensive analytics)
- **Charting Library**: For data visualization
- **Export Library**: For PDF/Excel generation

## 🎯 Business Value

- **Decision Making**: Data-driven insights for fleet optimization
- **Cost Optimization**: Identify cost-saving opportunities
- **Performance Improvement**: Track and improve operational efficiency
- **Competitive Advantage**: Better service through analytics
- **ROI Tracking**: Measure return on fleet investments

---

**Story Owner**: Fleet Management Team  
**Technical Lead**: Backend Team  
**Stakeholders**: Fleet Managers, Operations Team, Finance Team
