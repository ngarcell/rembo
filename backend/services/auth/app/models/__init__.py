# Models package
from .simple_vehicle import SimpleVehicle
from .simple_driver import SimpleDriver
from .vehicle_assignment import VehicleAssignment
from .vehicle_status import (
    VehicleStatusHistory,
    MaintenanceRecord,
    VehicleDocument,
    VehicleInspection,
)
from .fleet_analytics import (
    PerformanceMetric,
    RoutePerformance,
    VehiclePerformanceSummary,
    FleetKPI,
)
from .trip import (
    Route,
    Trip,
    TripTemplate,
    TripStatus,
)
from .booking import (
    Booking,
    Passenger,
    Payment,
    BookingStatus,
    PaymentStatus,
    PaymentMethod,
    SeatPreference,
)
