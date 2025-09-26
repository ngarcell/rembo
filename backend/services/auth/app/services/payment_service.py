"""
Payment service for business logic and payment management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.payment import (
    PaymentTransaction, 
    PaymentStatus, 
    RefundTransaction, 
    RefundStatus,
    RefundReason
)
from app.models.booking import Booking
from app.models.trip import Trip
from app.models.simple_vehicle import SimpleVehicle
from app.models.user_profile import UserProfile
from app.services.mpesa_service import MpesaService
from app.schemas.payment import (
    PaymentStatusResponse,
    PaymentListResponse,
    PaymentDashboardResponse,
    RefundStatusResponse
)

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment business logic"""
    
    def __init__(self):
        self.mpesa_service = MpesaService()
    
    async def validate_payment_request(
        self, 
        booking_id: str, 
        amount: Decimal, 
        user_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Validate payment request before processing"""
        try:
            # Check if booking exists and belongs to user
            booking = db.query(Booking).filter(
                and_(
                    Booking.id == booking_id,
                    or_(
                        Booking.passenger_id == user_id,
                        Booking.passenger_phone == user_id  # Allow phone-based lookup
                    )
                )
            ).first()
            
            if not booking:
                return False, {"error": "Booking not found or access denied"}
            
            # Check if booking is in valid state for payment
            if booking.booking_status in ["CANCELLED", "COMPLETED"]:
                return False, {"error": "Cannot pay for cancelled or completed booking"}
            
            # Check if payment amount matches booking amount
            if abs(float(amount) - float(booking.amount_due)) > 0.01:
                return False, {
                    "error": f"Payment amount {amount} does not match booking amount {booking.amount_due}"
                }
            
            # Check if booking already has a successful payment
            existing_payment = db.query(PaymentTransaction).filter(
                and_(
                    PaymentTransaction.booking_id == booking_id,
                    PaymentTransaction.status == "completed"
                )
            ).first()
            
            if existing_payment:
                return False, {"error": "Booking already paid"}
            
            # Check if there's a pending payment
            pending_payment = db.query(PaymentTransaction).filter(
                and_(
                    PaymentTransaction.booking_id == booking_id,
                    PaymentTransaction.status.in_([PaymentStatus.PENDING, PaymentStatus.PROCESSING]),
                    PaymentTransaction.expires_at > datetime.utcnow()
                )
            ).first()
            
            if pending_payment:
                return False, {
                    "error": "Payment already in progress",
                    "payment_id": str(pending_payment.id)
                }
            
            return True, {"booking": booking}
            
        except Exception as e:
            logger.error(f"Error validating payment request: {str(e)}")
            return False, {"error": "Payment validation failed"}
    
    async def get_payment_status(
        self, 
        payment_id: str, 
        user_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Get payment status with user access control"""
        try:
            # Get payment with booking info
            payment = db.query(PaymentTransaction).join(Booking).filter(
                and_(
                    PaymentTransaction.id == payment_id,
                    or_(
                        Booking.passenger_id == user_id,
                        Booking.passenger_phone == user_id
                    )
                )
            ).first()
            
            if not payment:
                return False, {"error": "Payment not found or access denied"}
            
            # Convert to response schema
            response = PaymentStatusResponse(
                payment_id=str(payment.id),
                booking_id=str(payment.booking_id),
                payment_reference=payment.payment_reference,
                phone_number=payment.phone_number,
                amount=payment.amount,
                status=payment.status,
                mpesa_receipt_number=payment.mpesa_receipt_number,
                transaction_date=payment.transaction_date,
                failure_reason=payment.failure_reason,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
                expires_at=payment.expires_at
            )
            
            return True, response.dict()
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return False, {"error": "Failed to get payment status"}
    
    async def list_payments(
        self,
        user_id: str,
        user_role: str,
        fleet_id: Optional[str],
        page: int,
        limit: int,
        status_filter: Optional[str] = None,
        booking_id: Optional[str] = None,
        db: Session = None
    ) -> Tuple[bool, Dict]:
        """List payments with pagination and filtering"""
        try:
            # Build base query based on user role
            if user_role == "manager" and fleet_id:
                # Manager can see all payments in their fleet
                query = db.query(PaymentTransaction).join(Booking).join(
                    UserProfile, Booking.passenger_id == UserProfile.id
                ).filter(UserProfile.fleet_id == fleet_id)
            else:
                # Regular user can only see their own payments
                query = db.query(PaymentTransaction).join(Booking).filter(
                    or_(
                        Booking.passenger_id == user_id,
                        Booking.passenger_phone == user_id
                    )
                )
            
            # Apply filters
            if status_filter:
                query = query.filter(PaymentTransaction.status == status_filter)
            
            if booking_id:
                query = query.filter(PaymentTransaction.booking_id == booking_id)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            payments = query.order_by(desc(PaymentTransaction.created_at)).offset(offset).limit(limit).all()
            
            # Convert to response format
            payment_responses = []
            for payment in payments:
                payment_responses.append(PaymentStatusResponse(
                    payment_id=str(payment.id),
                    booking_id=str(payment.booking_id),
                    payment_reference=payment.payment_reference,
                    phone_number=payment.phone_number,
                    amount=payment.amount,
                    status=payment.status,
                    mpesa_receipt_number=payment.mpesa_receipt_number,
                    transaction_date=payment.transaction_date,
                    failure_reason=payment.failure_reason,
                    created_at=payment.created_at,
                    updated_at=payment.updated_at,
                    expires_at=payment.expires_at
                ))
            
            response = PaymentListResponse(
                payments=payment_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_next=(offset + limit) < total_count,
                has_prev=page > 1
            )
            
            return True, response.dict()
            
        except Exception as e:
            logger.error(f"Error listing payments: {str(e)}")
            return False, {"error": "Failed to list payments"}
    
    async def get_payment_dashboard(
        self, 
        fleet_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Get payment dashboard data for managers"""
        try:
            # Get payments for the fleet through trip -> vehicle -> fleet relationship
            base_query = db.query(PaymentTransaction).join(Booking).join(
                Trip, Booking.trip_id == Trip.id
            ).join(
                SimpleVehicle, Trip.vehicle_id == SimpleVehicle.id
            ).filter(SimpleVehicle.fleet_id == fleet_id)
            
            # Calculate metrics
            total_payments = base_query.count()
            total_amount = base_query.filter(
                PaymentTransaction.status == "completed"
            ).with_entities(func.sum(PaymentTransaction.amount)).scalar() or Decimal('0')

            successful_payments = base_query.filter(
                PaymentTransaction.status == "completed"
            ).count()

            failed_payments = base_query.filter(
                PaymentTransaction.status == "failed"
            ).count()
            
            pending_payments = base_query.filter(
                PaymentTransaction.status.in_([PaymentStatus.PENDING, PaymentStatus.PROCESSING])
            ).count()
            
            success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
            average_amount = (total_amount / successful_payments) if successful_payments > 0 else Decimal('0')
            
            # Today's metrics
            today = datetime.utcnow().date()
            today_query = base_query.filter(
                func.date(PaymentTransaction.created_at) == today
            )
            
            today_payments = today_query.count()
            today_amount = today_query.filter(
                PaymentTransaction.status == "completed"
            ).with_entities(func.sum(PaymentTransaction.amount)).scalar() or Decimal('0')
            
            # Recent payments
            recent_payments_query = base_query.order_by(
                desc(PaymentTransaction.created_at)
            ).limit(10)
            
            recent_payments = []
            for payment in recent_payments_query.all():
                recent_payments.append(PaymentStatusResponse(
                    payment_id=str(payment.id),
                    booking_id=str(payment.booking_id),
                    payment_reference=payment.payment_reference,
                    phone_number=payment.phone_number,
                    amount=payment.amount,
                    status=payment.status,
                    mpesa_receipt_number=payment.mpesa_receipt_number,
                    transaction_date=payment.transaction_date,
                    failure_reason=payment.failure_reason,
                    created_at=payment.created_at,
                    updated_at=payment.updated_at,
                    expires_at=payment.expires_at
                ))
            
            response = PaymentDashboardResponse(
                total_payments=total_payments,
                total_amount=total_amount,
                successful_payments=successful_payments,
                failed_payments=failed_payments,
                pending_payments=pending_payments,
                success_rate=success_rate,
                average_amount=average_amount,
                today_payments=today_payments,
                today_amount=today_amount,
                recent_payments=recent_payments
            )
            
            return True, response.dict()
            
        except Exception as e:
            logger.error(f"Error getting payment dashboard: {str(e)}")
            return False, {"error": "Failed to get dashboard data"}
    
    async def schedule_payment_timeout_check(self, payment_id: str, timeout_seconds: int):
        """Schedule payment timeout check"""
        try:
            await asyncio.sleep(timeout_seconds)
            
            # Check if payment is still pending and mark as expired
            # This would typically be done with a proper task queue like Celery
            logger.info(f"Payment timeout check for {payment_id} - implement with task queue")
            
        except Exception as e:
            logger.error(f"Error in payment timeout check: {str(e)}")
    
    async def process_mpesa_callback(self, callback_data: Dict, db: Session):
        """Process M-Pesa callback in background"""
        try:
            success, result = await self.mpesa_service.handle_stk_callback(callback_data, db)
            if success:
                logger.info(f"M-Pesa callback processed successfully: {result}")
            else:
                logger.error(f"Failed to process M-Pesa callback: {result}")

        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {str(e)}")

    async def initiate_refund(
        self,
        payment_id: str,
        refund_amount: Decimal,
        refund_reason: RefundReason,
        refund_notes: Optional[str],
        manager_id: str,
        fleet_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Initiate refund for a payment"""
        try:
            # Get original payment
            payment = db.query(PaymentTransaction).filter(
                PaymentTransaction.id == payment_id
            ).first()

            if not payment:
                return False, {"error": "Payment not found"}

            # Verify payment belongs to manager's fleet
            booking = db.query(Booking).join(UserProfile).filter(
                and_(
                    Booking.id == payment.booking_id,
                    UserProfile.fleet_id == fleet_id
                )
            ).first()

            if not booking:
                return False, {"error": "Payment not found in your fleet"}

            # Validate refund amount
            if refund_amount > payment.amount:
                return False, {"error": "Refund amount cannot exceed payment amount"}

            # Check if payment is completed
            if payment.status != "completed":
                return False, {"error": "Can only refund completed payments"}

            # Create refund transaction
            refund = RefundTransaction(
                original_payment_id=payment.id,
                booking_id=payment.booking_id,
                refund_amount=refund_amount,
                refund_reason=refund_reason,
                refund_notes=refund_notes,
                processed_by=manager_id,
                requires_approval=refund_amount > Decimal('1000.00'),  # Require approval for large refunds
                status=RefundStatus.PENDING
            )

            db.add(refund)
            db.commit()

            # Convert to response
            response = RefundStatusResponse(
                refund_id=str(refund.id),
                original_payment_id=str(refund.original_payment_id),
                booking_id=str(refund.booking_id),
                refund_amount=refund.refund_amount,
                refund_reason=refund.refund_reason,
                refund_notes=refund.refund_notes,
                status=refund.status,
                requires_approval=refund.requires_approval,
                processed_by=str(refund.processed_by),
                created_at=refund.created_at,
                updated_at=refund.updated_at
            )

            return True, response.dict()

        except Exception as e:
            db.rollback()
            logger.error(f"Error initiating refund: {str(e)}")
            return False, {"error": "Failed to initiate refund"}

    async def get_refund_status(
        self,
        refund_id: str,
        user_id: str,
        user_role: str,
        fleet_id: Optional[str],
        db: Session
    ) -> Tuple[bool, Dict]:
        """Get refund status with access control"""
        try:
            # Build query based on user role
            if user_role == "manager" and fleet_id:
                refund = db.query(RefundTransaction).join(
                    Booking
                ).join(
                    UserProfile, Booking.passenger_id == UserProfile.id
                ).filter(
                    and_(
                        RefundTransaction.id == refund_id,
                        UserProfile.fleet_id == fleet_id
                    )
                ).first()
            else:
                refund = db.query(RefundTransaction).join(Booking).filter(
                    and_(
                        RefundTransaction.id == refund_id,
                        or_(
                            Booking.passenger_id == user_id,
                            Booking.passenger_phone == user_id
                        )
                    )
                ).first()

            if not refund:
                return False, {"error": "Refund not found or access denied"}

            # Convert to response
            response = RefundStatusResponse(
                refund_id=str(refund.id),
                original_payment_id=str(refund.original_payment_id),
                booking_id=str(refund.booking_id),
                refund_amount=refund.refund_amount,
                refund_reason=refund.refund_reason,
                refund_notes=refund.refund_notes,
                status=refund.status,
                mpesa_transaction_id=refund.mpesa_transaction_id,
                requires_approval=refund.requires_approval,
                approved_by=str(refund.approved_by) if refund.approved_by else None,
                approved_at=refund.approved_at,
                processed_by=str(refund.processed_by) if refund.processed_by else None,
                processed_at=refund.processed_at,
                completed_at=refund.completed_at,
                failure_reason=refund.failure_reason,
                created_at=refund.created_at,
                updated_at=refund.updated_at
            )

            return True, response.dict()

        except Exception as e:
            logger.error(f"Error getting refund status: {str(e)}")
            return False, {"error": "Failed to get refund status"}

    async def query_payment_status(
        self,
        payment_id: Optional[str],
        payment_reference: Optional[str],
        user_id: str,
        db: Session
    ) -> Tuple[bool, Dict]:
        """Query payment status by ID or reference"""
        try:
            # Build query
            query = db.query(PaymentTransaction).join(Booking)

            if payment_id:
                query = query.filter(PaymentTransaction.id == payment_id)
            elif payment_reference:
                query = query.filter(PaymentTransaction.payment_reference == payment_reference)
            else:
                return False, {"error": "Payment ID or reference required"}

            # Add user access control
            query = query.filter(
                or_(
                    Booking.passenger_id == user_id,
                    Booking.passenger_phone == user_id
                )
            )

            payment = query.first()

            if not payment:
                return False, {"error": "Payment not found or access denied"}

            # If payment is still processing, try to query M-Pesa
            if (payment.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING] and
                payment.checkout_request_id):

                success, mpesa_result = await self.mpesa_service.query_stk_push_status(
                    payment.checkout_request_id, db
                )

                if success:
                    # Update payment status based on M-Pesa response
                    result_code = mpesa_result.get("ResultCode")
                    if result_code == "0":
                        payment.status = "completed"
                        payment.transaction_date = datetime.utcnow()
                    elif result_code in ["1032", "1037"]:  # User cancelled or timeout
                        payment.status = "cancelled"

                    db.commit()

            # Convert to response
            response = PaymentStatusResponse(
                payment_id=str(payment.id),
                booking_id=str(payment.booking_id),
                payment_reference=payment.payment_reference,
                phone_number=payment.phone_number,
                amount=payment.amount,
                status=payment.status,
                mpesa_receipt_number=payment.mpesa_receipt_number,
                transaction_date=payment.transaction_date,
                failure_reason=payment.failure_reason,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
                expires_at=payment.expires_at
            )

            return True, response.dict()

        except Exception as e:
            logger.error(f"Error querying payment status: {str(e)}")
            return False, {"error": "Failed to query payment status"}
