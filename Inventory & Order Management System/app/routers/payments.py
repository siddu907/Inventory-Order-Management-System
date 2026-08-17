from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import PaymentService
from app.background.notification_tasks import notify_payment_completed, notify_payment_refunded

router = APIRouter()


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = PaymentService(db).create_payment(
        order_id=payload.order_id,
        payment_method=payload.payment_method,
        requesting_user_id=current_user.id,
        requesting_role=current_user.role,
    )

    # Trigger payment notification (in-app + email) for Customer and Admin
    background_tasks.add_task(
        notify_payment_completed,
        order_id=payment.order_id,
        customer_id=current_user.id,
        amount=payment.amount,
        method=payment.payment_method,
        payment_id=payment.id  # ← Added payment_id
    )
    
    return payment


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PaymentService(db).get_payment(payment_id, current_user.id, current_user.role)


@router.post("/{payment_id}/refund", response_model=PaymentOut)
def refund_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = PaymentService(db).refund_payment(payment_id, current_user.id, current_user.role)
    
    # Trigger refund notification (in-app + email) for Customer
    if hasattr(payment, 'customer_id') and payment.customer_id:
        background_tasks.add_task(
            notify_payment_refunded,
            order_id=payment.order_id,
            customer_id=payment.customer_id,
            amount=payment.amount,
            method=payment.payment_method,
            payment_id=payment.id  # ← Added payment_id
        )
    
    return payment
