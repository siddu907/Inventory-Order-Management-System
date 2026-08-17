from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentRepository(db)
        self.order_repo = OrderRepository(db)

    def create_payment(self, order_id: int, payment_method: str,  requesting_user_id: int, requesting_role: str) -> Payment:
        # Only customers can create payments
        if requesting_role != "Customer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only customers can make payments")
        
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
        if order.customer_id != requesting_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed to pay for this order")
        if order.status == "Cancelled":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Cannot pay for a cancelled order")

        # prevent duplicate payment
        existing = self.repo.get_by_order_id(order_id)
        if existing and existing.status == "Paid":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Order has already been paid")

        method_map = {"cash": "Cash", "card": "Card", "upi": "UPI", "online": "Online"}
        norm = method_map.get(payment_method.strip().lower(), payment_method.strip().title())

        if existing:
            existing.payment_method = norm
            existing.status = "Paid"
            existing.payment_date = datetime.utcnow()
            payment = self.repo.update(existing)
        else:
            payment = Payment(
                order_id=order_id,
                amount=order.total_amount,
                payment_method=norm,
                status="Paid",
                payment_date=datetime.utcnow(),
            )
            payment = self.repo.create(payment)

        # auto-confirm order on payment
        if order.status == "Pending":
            order.status = "Confirmed"
            self.db.commit()

        return payment

    def get_payment(self, payment_id: int,
                    requesting_user_id: int, requesting_role: str) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment not found")
        if requesting_role == "Customer":
            order = self.order_repo.get_by_id(payment.order_id)
            if not order or order.customer_id != requesting_user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return payment

    def refund_payment(self, payment_id: int,
                       requesting_user_id: int, requesting_role: str) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment not found")
        if requesting_role not in {"Admin", "Staff"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin or Staff can refund payments")
        if payment.status != "Paid":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only paid payments can be refunded")
        
        payment.status = "Refunded"
        payment.payment_date = datetime.utcnow()
        updated_payment = self.repo.update(payment)
        
        # Get customer_id from order for notification
        order = self.order_repo.get_by_id(payment.order_id)
        if order:
            updated_payment.customer_id = order.customer_id  # Add customer_id attribute
        
        return updated_payment
