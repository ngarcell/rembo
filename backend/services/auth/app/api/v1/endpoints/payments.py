"""
Payment API endpoints for M-Pesa integration
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user, require_manager
from app.models.user_profile import UserProfile
from app.services.mpesa_service import MpesaService
from app.services.payment_service import PaymentService
from app.schemas.payment import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentStatusRequest,
    PaymentStatusResponse,
    PaymentListResponse,
    PaymentDashboardResponse,
    MpesaCallbackRequest,
    MpesaCallbackResponse,
    RefundInitiateRequest,
    RefundStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()
mpesa_service = MpesaService()
payment_service = PaymentService()


@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    request: PaymentInitiateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Initiate M-Pesa STK Push payment
    
    - **booking_id**: ID of the booking to pay for
    - **phone_number**: Phone number for M-Pesa payment
    - **amount**: Payment amount in KES
    """
    try:
        # Validate booking and user permissions
        success, validation_result = await payment_service.validate_payment_request(
            request.booking_id, request.amount, current_user.id, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.get("error", "Payment validation failed")
            )
        
        # Initiate STK Push
        success, result = await mpesa_service.initiate_stk_push(
            phone_number=request.phone_number,
            amount=request.amount,
            booking_id=request.booking_id,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to initiate payment")
            )
        
        # Schedule payment timeout check
        background_tasks.add_task(
            payment_service.schedule_payment_timeout_check,
            result["payment_id"],
            120  # 2 minutes timeout
        )
        
        return PaymentInitiateResponse(
            success=True,
            payment_id=result["payment_id"],
            checkout_request_id=result.get("checkout_request_id"),
            merchant_request_id=result.get("merchant_request_id"),
            payment_reference=result["payment_reference"],
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in initiate_payment endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/status/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get payment status by payment ID
    """
    try:
        success, result = await payment_service.get_payment_status(
            payment_id=payment_id,
            user_id=current_user.id,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Payment not found")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_payment_status endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/query-status")
async def query_payment_status(
    request: PaymentStatusRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Query payment status from M-Pesa API
    """
    try:
        if request.checkout_request_id:
            success, result = await mpesa_service.query_stk_push_status(
                checkout_request_id=request.checkout_request_id,
                db=db
            )
        else:
            success, result = await payment_service.query_payment_status(
                payment_id=request.payment_id,
                payment_reference=request.payment_reference,
                user_id=current_user.id,
                db=db
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to query payment status")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query_payment_status endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/list", response_model=PaymentListResponse)
async def list_payments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by payment status"),
    booking_id: Optional[str] = Query(None, description="Filter by booking ID"),
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    List payments for current user or manager's fleet
    """
    try:
        success, result = await payment_service.list_payments(
            user_id=current_user.id,
            user_role=current_user.role,
            fleet_id=getattr(current_user, 'fleet_id', None),
            page=page,
            limit=limit,
            status_filter=status_filter,
            booking_id=booking_id,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to list payments")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_payments endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/dashboard", response_model=PaymentDashboardResponse)
async def get_payment_dashboard(
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Get payment dashboard data for managers
    """
    try:
        success, result = await payment_service.get_payment_dashboard(
            fleet_id=str(manager.fleet_id),
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to get dashboard data")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_payment_dashboard endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/mpesa/callback", response_model=MpesaCallbackResponse)
async def mpesa_callback(
    callback_data: MpesaCallbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    M-Pesa STK Push callback endpoint
    
    This endpoint receives callbacks from M-Pesa after payment processing
    """
    try:
        logger.info(f"Received M-Pesa callback: {callback_data.dict()}")
        
        # Process callback in background to respond quickly to M-Pesa
        background_tasks.add_task(
            payment_service.process_mpesa_callback,
            callback_data.dict(),
            db
        )
        
        # Return success response to M-Pesa
        return MpesaCallbackResponse(
            ResultCode=0,
            ResultDesc="Success"
        )
        
    except Exception as e:
        logger.error(f"Error in mpesa_callback endpoint: {str(e)}")
        # Still return success to M-Pesa to avoid retries
        return MpesaCallbackResponse(
            ResultCode=0,
            ResultDesc="Success"
        )


@router.post("/refund", response_model=RefundStatusResponse)
async def initiate_refund(
    request: RefundInitiateRequest,
    db: Session = Depends(get_db),
    manager: UserProfile = Depends(require_manager),
):
    """
    Initiate refund for a payment (Manager only)
    """
    try:
        success, result = await payment_service.initiate_refund(
            payment_id=request.payment_id,
            refund_amount=request.refund_amount,
            refund_reason=request.refund_reason,
            refund_notes=request.refund_notes,
            manager_id=str(manager.id),
            fleet_id=str(manager.fleet_id),
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to initiate refund")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in initiate_refund endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/refund/{refund_id}", response_model=RefundStatusResponse)
async def get_refund_status(
    refund_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get refund status by refund ID
    """
    try:
        success, result = await payment_service.get_refund_status(
            refund_id=refund_id,
            user_id=current_user.id,
            user_role=current_user.role,
            fleet_id=getattr(current_user, 'fleet_id', None),
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Refund not found")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_refund_status endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
