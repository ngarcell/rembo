#!/usr/bin/env python3
"""
Test M-Pesa STK Push integration directly
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
from app.models.booking import Booking


async def test_stk_push():
    """Test STK Push integration with real booking"""
    print("🚀 Testing M-Pesa STK Push Integration...")
    
    try:
        # Initialize M-Pesa service
        mpesa_service = MpesaService()
        
        # Test 1: Verify M-Pesa configuration
        print("\n1. Testing M-Pesa Configuration...")
        print(f"   Environment: {mpesa_service.base_url}")
        print(f"   Business Short Code: {mpesa_service.business_short_code}")
        print(f"   Callback URL: {mpesa_service.callback_url}")
        
        # Test 2: Get access token
        print("\n2. Testing Access Token Generation...")
        access_token = await mpesa_service.get_access_token()
        if access_token:
            print("   ✅ Access token generated successfully")
            print(f"   Token: {access_token[:20]}...")
        else:
            print("   ❌ Failed to generate access token")
            return False
        
        # Test 3: Get database connection and booking
        print("\n3. Testing Database Connection and Booking...")
        db = next(get_db())
        
        # Use the existing booking
        booking_id = "b3b94de8-4f6a-4567-b781-7877c1e55a42"
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            print(f"   ❌ Booking {booking_id} not found")
            return False
        
        print(f"   ✅ Found booking: {booking.booking_reference}")
        print(f"   Amount due: KES {booking.amount_due}")
        print(f"   Status: {booking.booking_status}")
        print(f"   Passenger phone: {booking.passenger_phone}")
        
        # Test 4: Initiate STK Push
        print("\n4. Testing STK Push Initiation...")
        
        # Use sandbox test phone number
        test_phone = "254708374149"  # Safaricom sandbox test number
        amount = Decimal("1.00")  # Minimum amount for testing
        
        print(f"   Using test phone: {test_phone}")
        print(f"   Test amount: KES {amount}")
        print(f"   Booking ID: {booking_id}")
        
        success, result = await mpesa_service.initiate_stk_push(
            phone_number=test_phone,
            amount=amount,
            booking_id=booking_id,
            db=db
        )
        
        if success:
            print("   ✅ STK Push initiated successfully!")
            print(f"   Payment ID: {result['payment_id']}")
            print(f"   Checkout Request ID: {result.get('checkout_request_id')}")
            print(f"   Message: {result['message']}")
            
            # Test 5: Query payment status
            print("\n5. Testing Payment Status Query...")
            print("   Waiting 5 seconds before status check...")
            await asyncio.sleep(5)
            
            if result.get('checkout_request_id'):
                status_success, status_result = await mpesa_service.query_stk_push_status(
                    checkout_request_id=result['checkout_request_id'],
                    db=db
                )
                
                if status_success:
                    print("   ✅ Status query successful")
                    print(f"   Result: {json.dumps(status_result, indent=2)}")
                else:
                    print(f"   ⚠️  Status query result: {status_result}")
            
            # Test 6: Check payment record in database
            print("\n6. Testing Payment Record...")
            from app.models.payment import PaymentTransaction
            payment = db.query(PaymentTransaction).filter(
                PaymentTransaction.id == result['payment_id']
            ).first()
            
            if payment:
                print("   ✅ Payment record created in database")
                print(f"   Payment Reference: {payment.payment_reference}")
                print(f"   Status: {payment.status}")
                print(f"   Amount: KES {payment.amount}")
                print(f"   Phone: {payment.phone_number}")
                print(f"   Created: {payment.created_at}")
            else:
                print("   ❌ Payment record not found in database")
            
        else:
            print(f"   ❌ STK Push failed: {result.get('error')}")
            return False
        
        db.close()
        
        print("\n🎉 STK Push test completed successfully!")
        print("\n📱 **NEXT STEPS FOR COMPLETE TESTING:**")
        print("   1. Check your phone (254708374149) for M-Pesa prompt")
        print("   2. Enter M-Pesa PIN to complete payment")
        print("   3. Check callback handling in application logs")
        print("   4. Verify payment status updates in database")
        
        return True
        
    except Exception as e:
        print(f"   ❌ STK Push test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🏦 M-Pesa STK Push Integration Test")
    print("=" * 50)
    
    success = await test_stk_push()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ STK Push integration test PASSED!")
        print("🎯 M-Pesa integration is working correctly")
    else:
        print("❌ STK Push integration test FAILED!")
        print("🔧 Check configuration and try again")


if __name__ == "__main__":
    asyncio.run(main())
