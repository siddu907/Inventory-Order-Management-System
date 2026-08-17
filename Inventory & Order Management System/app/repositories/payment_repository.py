from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.order import Order


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_order_id(self, order_id: int) -> Payment | None:
        return self.db.query(Payment).filter(Payment.order_id == order_id).first()

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_all(self, skip: int = 0, limit: int = 100,
                customer_id: int | None = None) -> list[Payment]:
        q = self.db.query(Payment)
        if customer_id is not None:
            q = q.join(Order).filter(Order.customer_id == customer_id)
        return q.offset(skip).limit(limit).all()

    def update(self, payment: Payment) -> Payment:
        self.db.commit()
        self.db.refresh(payment)
        return payment
