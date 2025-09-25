#!/usr/bin/env python3
"""
Test script to debug booking creation
"""
import requests
import json
import time

def test_booking():
    """Test booking creation"""
    
    # Test data
    booking_data = {
        "trip_id": "d21911f5-c638-4877-a65b-9c59cb1072d5",
        "seats_booked": 1,
        "seat_numbers": ["1"],
        "passenger_name": "John Doe",
        "passenger_phone": "+254712345678",
        "payment_method": "mpesa"
    }
    
    print("Testing booking creation...")
    print(f"Data: {json.dumps(booking_data, indent=2)}")
    
    try:
        # Make the request with a timeout
        response = requests.post(
            "http://localhost:8001/api/v1/passenger/bookings",
            json=booking_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Booking created successfully!")
            return response.json()
        else:
            print(f"❌ Booking failed with status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    test_booking()
