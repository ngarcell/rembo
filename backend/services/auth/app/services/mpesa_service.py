"""
M-Pesa Daraja API service for STK Push and B2C transactions
"""

import base64
import json
import logging
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional, Tuple
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.payment import PaymentTransaction, PaymentStatus, PaymentWebhookLog
from app.models.booking import Booking

logger = logging.getLogger(__name__)


class MpesaService:
    """M-Pesa Daraja API service"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_short_code = settings.MPESA_BUSINESS_SHORT_CODE
        self.lipa_na_mpesa_passkey = settings.MPESA_LIPA_NA_MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        # API URLs (sandbox vs production)
        if settings.MPESA_ENVIRONMENT == "production":
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"
            
        self.auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        self.stk_query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        self.b2c_url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
        
        self._access_token = None
        self._token_expires_at = None
    
    async def get_access_token(self) -> Optional[str]:
        """Get OAuth access token from M-Pesa API"""
        try:
            # Check if current token is still valid
            if (self._access_token and self._token_expires_at and 
                datetime.now() < self._token_expires_at):
                return self._access_token
            
            # Generate credentials
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.auth_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data.get("access_token")
                    expires_in = int(data.get("expires_in", 3600))
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    logger.info("M-Pesa access token obtained successfully")
                    return self._access_token
                else:
                    logger.error(f"Failed to get M-Pesa access token: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting M-Pesa access token: {str(e)}")
            return None
    
    def generate_password(self) -> str:
        """Generate password for STK Push request"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_string = f"{self.business_short_code}{self.lipa_na_mpesa_passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password
    
    def generate_timestamp(self) -> str:
        """Generate timestamp for M-Pesa requests"""
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def generate_payment_reference(self) -> str:
        """Generate unique payment reference"""
        random_part = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
        )
        return f"PAY-{random_part}"
    
    async def initiate_stk_push(
        self, 
        phone_number: str, 
        amount: Decimal, 
        booking_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Initiate STK Push payment request"""
        try:
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                return False, {"error": "Failed to get M-Pesa access token"}
            
            # Normalize phone number (remove + and ensure 254 prefix)
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif not phone_number.startswith("254"):
                phone_number = "254" + phone_number
            
            # Generate payment reference and other required fields
            payment_reference = self.generate_payment_reference()
            timestamp = self.generate_timestamp()
            password = self.generate_password()
            
            # Prepare STK Push request
            stk_request = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  # M-Pesa expects integer
                "PartyA": phone_number,
                "PartyB": self.business_short_code,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": payment_reference,
                "TransactionDesc": f"Payment for booking {booking_id}"
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Create payment transaction record
            payment_transaction = PaymentTransaction(
                booking_id=booking_id,
                phone_number=phone_number,
                amount=amount,
                payment_reference=payment_reference,
                account_reference=payment_reference,
                transaction_desc=f"Payment for booking {booking_id}",
                status="pending",
                expires_at=datetime.utcnow() + timedelta(minutes=2)  # 2 minute timeout
            )
            
            db.add(payment_transaction)
            db.flush()  # Get the ID without committing
            
            # Make STK Push request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.stk_push_url, 
                    json=stk_request, 
                    headers=headers
                )
                
                response_data = response.json()
                
                if response.status_code == 200 and response_data.get("ResponseCode") == "0":
                    # Success - update payment transaction
                    payment_transaction.checkout_request_id = response_data.get("CheckoutRequestID")
                    payment_transaction.merchant_request_id = response_data.get("MerchantRequestID")
                    payment_transaction.status = "processing"
                    payment_transaction.gateway_response = json.dumps(response_data)
                    
                    db.commit()
                    
                    logger.info(f"STK Push initiated successfully for payment {payment_reference}")
                    
                    return True, {
                        "payment_id": str(payment_transaction.id),
                        "checkout_request_id": response_data.get("CheckoutRequestID"),
                        "merchant_request_id": response_data.get("MerchantRequestID"),
                        "payment_reference": payment_reference,
                        "message": "STK Push sent to your phone. Please enter your M-Pesa PIN to complete payment."
                    }
                else:
                    # Failed - update payment transaction
                    error_message = response_data.get("errorMessage", "STK Push failed")
                    payment_transaction.status = "failed"
                    payment_transaction.failure_reason = error_message
                    payment_transaction.gateway_response = json.dumps(response_data)
                    
                    db.commit()
                    
                    logger.error(f"STK Push failed for payment {payment_reference}: {error_message}")
                    
                    return False, {
                        "error": error_message,
                        "payment_id": str(payment_transaction.id)
                    }
                    
        except Exception as e:
            db.rollback()
            error_msg = f"Error initiating STK Push: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
    
    async def query_stk_push_status(
        self, 
        checkout_request_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Query STK Push payment status"""
        try:
            # Get access token
            access_token = await self.get_access_token()
            if not access_token:
                return False, {"error": "Failed to get M-Pesa access token"}
            
            # Prepare query request
            timestamp = self.generate_timestamp()
            password = self.generate_password()
            
            query_request = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make query request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.stk_query_url,
                    json=query_request,
                    headers=headers
                )
                
                response_data = response.json()
                
                if response.status_code == 200:
                    return True, response_data
                else:
                    logger.error(f"STK Push query failed: {response.text}")
                    return False, {"error": "Failed to query payment status"}
                    
        except Exception as e:
            error_msg = f"Error querying STK Push status: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
    
    async def handle_stk_callback(
        self, 
        callback_data: Dict,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Handle STK Push callback from M-Pesa"""
        try:
            # Log the webhook
            webhook_log = PaymentWebhookLog(
                webhook_type="stk_push",
                raw_payload=json.dumps(callback_data),
                processed=False
            )
            db.add(webhook_log)
            db.flush()
            
            # Extract callback data
            stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")
            
            if not checkout_request_id:
                logger.error("No CheckoutRequestID in callback")
                return False, {"error": "Invalid callback data"}
            
            # Find payment transaction
            payment = db.query(PaymentTransaction).filter(
                PaymentTransaction.checkout_request_id == checkout_request_id
            ).first()
            
            if not payment:
                logger.error(f"Payment not found for CheckoutRequestID: {checkout_request_id}")
                return False, {"error": "Payment not found"}
            
            webhook_log.checkout_request_id = checkout_request_id
            
            # Process callback based on result code
            if result_code == 0:  # Success
                # Extract transaction details
                callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                metadata_dict = {item["Name"]: item.get("Value") for item in callback_metadata}
                
                # Update payment transaction
                payment.status = "completed"
                payment.mpesa_receipt_number = metadata_dict.get("MpesaReceiptNumber")
                payment.transaction_date = datetime.utcnow()
                payment.gateway_response = json.dumps(callback_data)
                
                # Update booking status
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking:
                    booking.payment_status = "COMPLETED"
                    booking.amount_paid = payment.amount
                    booking.booking_status = "CONFIRMED"
                
                webhook_log.processed = True
                webhook_log.processed_at = datetime.utcnow()
                
                db.commit()
                
                logger.info(f"Payment completed successfully: {payment.payment_reference}")
                
                return True, {
                    "status": "completed",
                    "payment_id": str(payment.id),
                    "mpesa_receipt": metadata_dict.get("MpesaReceiptNumber")
                }
                
            else:  # Failed
                payment.status = "failed"
                payment.failure_reason = result_desc
                payment.gateway_response = json.dumps(callback_data)
                
                webhook_log.processed = True
                webhook_log.processed_at = datetime.utcnow()
                
                db.commit()
                
                logger.info(f"Payment failed: {payment.payment_reference} - {result_desc}")
                
                return True, {
                    "status": "failed",
                    "payment_id": str(payment.id),
                    "reason": result_desc
                }
                
        except Exception as e:
            db.rollback()
            if 'webhook_log' in locals():
                webhook_log.processing_error = str(e)
                db.commit()
            
            error_msg = f"Error handling STK callback: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
