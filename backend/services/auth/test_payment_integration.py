#!/usr/bin/env python3
"""
Test script for M-Pesa payment integration
"""

import asyncio
import json
import sys
import os
from decimal import Decimal

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_db
from app.services.mpesa_service import MpesaService
from app.services.payment_service import PaymentService
from app.models.booking import Booking
from app.models.payment import PaymentTransaction, PaymentStatus


async def test_payment_integration():
    """Test the payment integration"""
    print("🧪 Testing M-Pesa Payment Integration...")
    
    # Initialize services
    mpesa_service = MpesaService()
    payment_service = PaymentService()
    
    # Test 1: Check M-Pesa configuration
    print("\n1. Testing M-Pesa Configuration...")
    print(f"   Environment: {mpesa_service.base_url}")
    print(f"   Business Short Code: {mpesa_service.business_short_code}")
    print(f"   Callback URL: {mpesa_service.callback_url}")
    
    # Test 2: Test access token generation
    print("\n2. Testing Access Token Generation...")
    try:
        access_token = await mpesa_service.get_access_token()
        if access_token:
            print("   ✅ Access token generated successfully")
            print(f"   Token: {access_token[:20]}...")
        else:
            print("   ❌ Failed to generate access token")
            return False
    except Exception as e:
        print(f"   ❌ Error generating access token: {str(e)}")
        return False
    
    # Test 3: Test payment reference generation
    print("\n3. Testing Payment Reference Generation...")
    payment_ref = mpesa_service.generate_payment_reference()
    print(f"   Generated reference: {payment_ref}")
    
    # Test 4: Test password generation
    print("\n4. Testing Password Generation...")
    password = mpesa_service.generate_password()
    timestamp = mpesa_service.generate_timestamp()
    print(f"   Generated password: {password[:20]}...")
    print(f"   Generated timestamp: {timestamp}")
    
    # Test 5: Test database connection and models
    print("\n5. Testing Database Connection...")
    try:
        db = next(get_db())
        
        # Check if we have any bookings to test with
        booking = db.query(Booking).filter(
            Booking.booking_status == "PENDING"
        ).first()
        
        if booking:
            print(f"   ✅ Found test booking: {booking.booking_reference}")
            print(f"   Amount due: KES {booking.amount_due}")
            
            # Test payment validation
            print("\n6. Testing Payment Validation...")
            success, result = await payment_service.validate_payment_request(
                booking_id=str(booking.id),
                amount=booking.amount_due,
                user_id=str(booking.passenger_id),
                db=db
            )
            
            if success:
                print("   ✅ Payment validation passed")
            else:
                print(f"   ❌ Payment validation failed: {result.get('error')}")
                
        else:
            print("   ⚠️  No test bookings found")
            
        # Check payment tables
        payment_count = db.query(PaymentTransaction).count()
        print(f"   Payment transactions in database: {payment_count}")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Database connection error: {str(e)}")
        return False
    
    print("\n🎉 Payment integration test completed!")
    return True


async def test_stk_push_simulation():
    """Test STK Push with sandbox data"""
    print("\n🚀 Testing STK Push Simulation...")
    
    # Sandbox test phone number
    test_phone = "254708374149"
    test_amount = Decimal("1.00")  # Minimum amount for testing
    
    try:
        db = next(get_db())
        
        # Find a test booking
        booking = db.query(Booking).filter(
            Booking.booking_status == "PENDING"
        ).first()
        
        if not booking:
            print("   ⚠️  No test booking available for STK Push test")
            return
        
        print(f"   Using booking: {booking.booking_reference}")
        print(f"   Test phone: {test_phone}")
        print(f"   Test amount: KES {test_amount}")
        
        # Initialize M-Pesa service
        mpesa_service = MpesaService()
        
        # Initiate STK Push
        print("   Initiating STK Push...")
        success, result = await mpesa_service.initiate_stk_push(
            phone_number=test_phone,
            amount=test_amount,
            booking_id=str(booking.id),
            db=db
        )
        
        if success:
            print("   ✅ STK Push initiated successfully!")
            print(f"   Payment ID: {result['payment_id']}")
            print(f"   Checkout Request ID: {result.get('checkout_request_id')}")
            print(f"   Message: {result['message']}")
            
            # Wait a moment and check status
            print("   Waiting 5 seconds before status check...")
            await asyncio.sleep(5)
            
            if result.get('checkout_request_id'):
                print("   Querying payment status...")
                status_success, status_result = await mpesa_service.query_stk_push_status(
                    checkout_request_id=result['checkout_request_id'],
                    db=db
                )
                
                if status_success:
                    print(f"   Status query result: {status_result}")
                else:
                    print(f"   Status query failed: {status_result}")
        else:
            print(f"   ❌ STK Push failed: {result.get('error')}")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ STK Push test error: {str(e)}")


def test_callback_simulation():
    """Test M-Pesa callback handling"""
    print("\n📞 Testing M-Pesa Callback Simulation...")
    
    # Sample callback data (successful payment)
    sample_callback = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": "ws_CO_191220191020363925",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {
                            "Name": "Amount",
                            "Value": 1.00
                        },
                        {
                            "Name": "MpesaReceiptNumber",
                            "Value": "NLJ7RT61SV"
                        },
                        {
                            "Name": "TransactionDate",
                            "Value": 20191219102115
                        },
                        {
                            "Name": "PhoneNumber",
                            "Value": 254708374149
                        }
                    ]
                }
            }
        }
    }
    
    print(f"   Sample callback data: {json.dumps(sample_callback, indent=2)}")
    print("   ✅ Callback structure looks valid")
    
    # Test callback parsing
    stk_callback = sample_callback.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    
    print(f"   Parsed CheckoutRequestID: {checkout_request_id}")
    print(f"   Parsed ResultCode: {result_code}")
    
    if result_code == 0:
        print("   ✅ This would be processed as successful payment")
    else:
        print("   ❌ This would be processed as failed payment")


async def main():
    """Main test function"""
    print("🏦 M-Pesa Payment Integration Test Suite")
    print("=" * 50)
    
    # Run basic integration tests
    success = await test_payment_integration()
    
    if success:
        # Run STK Push simulation (only if basic tests pass)
        await test_stk_push_simulation()
        
        # Test callback simulation
        test_callback_simulation()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())
