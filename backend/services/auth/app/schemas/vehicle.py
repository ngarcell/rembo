"""
Pydantic schemas for vehicle operations
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


class VehicleRegistrationRequest(BaseModel):
    """Simplified vehicle registration request - Essential fields only"""

    # Core Vehicle Information
    fleet_number: str = Field(..., min_length=1, max_length=20, description="Fleet number (unique within fleet)")
    license_plate: str = Field(..., min_length=1, max_length=20, description="License plate (unique across system)")
    capacity: int = Field(..., ge=1, le=100, description="Passenger capacity")
    route: str = Field(..., max_length=200, description="Assigned route")

    # GPS Credentials (Essential for tracking)
    gps_device_id: Optional[str] = Field(None, max_length=100, description="GPS device identifier")
    sim_number: Optional[str] = Field(None, max_length=20, description="SIM card number")
    gps_api_key: Optional[str] = Field(None, description="GPS API key (will be encrypted)")

    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: str) -> str:
        """Validate Kenyan license plate format"""
        if not v:
            raise ValueError("License plate is required")
        
        # Remove spaces and convert to uppercase
        v = v.replace(" ", "").upper()
        
        # Kenyan license plate patterns:
        # KXX 123X (new format)
        # KXX 123XX (some variations)
        patterns = [
            r'^K[A-Z]{2}[0-9]{3}[A-Z]$',      # KXX 123X
            r'^K[A-Z]{2}[0-9]{3}[A-Z]{2}$',   # KXX 123XX
            r'^[A-Z]{3}[0-9]{3}[A-Z]$',       # XXX 123X (older format)
        ]
        
        if not any(re.match(pattern, v) for pattern in patterns):
            raise ValueError("Invalid license plate format. Expected Kenyan format (e.g., KCA123A)")
        
        return v

    @field_validator('fleet_number')
    @classmethod
    def validate_fleet_number(cls, v: str) -> str:
        """Validate fleet number format"""
        if not v:
            raise ValueError("Fleet number is required")
        
        # Allow alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError("Fleet number can only contain letters, numbers, hyphens, and underscores")
        
        return v.upper()

    @field_validator('sim_number')
    @classmethod
    def validate_sim_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate SIM number format (Kenyan mobile format)"""
        if not v:
            return v
        
        # Remove spaces and special characters
        v = re.sub(r'[\s\-\(\)]', '', v)
        
        # Kenyan mobile number patterns
        patterns = [
            r'^254[17][0-9]{8}$',     # +254 7XX XXX XXX or +254 1XX XXX XXX
            r'^07[0-9]{8}$',          # 07XX XXX XXX
            r'^01[0-9]{8}$',          # 01XX XXX XXX
        ]
        
        if not any(re.match(pattern, v) for pattern in patterns):
            raise ValueError("Invalid SIM number format. Expected Kenyan mobile format")
        
        return v




class VehicleUpdateRequest(BaseModel):
    """Simplified vehicle update request - Essential fields only"""

    # Core Vehicle Information
    fleet_number: Optional[str] = Field(None, min_length=1, max_length=20)
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, ge=1, le=100)
    route: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, description="Vehicle status")

    # GPS Credentials
    gps_device_id: Optional[str] = Field(None, max_length=100)
    sim_number: Optional[str] = Field(None, max_length=20)

    # Apply same validators as registration
    validate_license_plate = field_validator('license_plate')(VehicleRegistrationRequest.validate_license_plate)
    validate_fleet_number = field_validator('fleet_number')(VehicleRegistrationRequest.validate_fleet_number)
    validate_sim_number = field_validator('sim_number')(VehicleRegistrationRequest.validate_sim_number)


class VehicleResponse(BaseModel):
    """Simplified vehicle response - Essential fields only"""

    id: str
    fleet_id: str
    manager_id: Optional[str]
    fleet_number: str
    license_plate: str
    capacity: int
    route: Optional[str]
    status: str
    gps_device_id: Optional[str]
    sim_number: Optional[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str]


class VehicleSummaryResponse(BaseModel):
    """Simplified vehicle summary response - Essential fields only"""

    id: str
    fleet_number: str
    license_plate: str
    capacity: int
    route: Optional[str]
    status: str
    created_at: str


class VehicleRegistrationResponse(BaseModel):
    """Schema for vehicle registration response"""
    
    success: bool
    message: str
    vehicle: VehicleResponse


class VehicleListResponse(BaseModel):
    """Schema for vehicle list response"""
    
    vehicles: List[VehicleSummaryResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


class VehicleDetailsResponse(BaseModel):
    """Schema for vehicle details response"""
    
    success: bool
    vehicle: VehicleResponse
    fleet_name: Optional[str] = None
