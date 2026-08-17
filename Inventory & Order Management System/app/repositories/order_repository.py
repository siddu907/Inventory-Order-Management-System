from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_by_id(self, order_id: int) -> Order | None:
        return self.db.query(Order).filter(
            Order.id == order_id, Order.is_deleted.is_(False)
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100,
                customer_id: int | None = None, status: str | None = None) -> list[Order]:
        q = self.db.query(Order).filter(Order.is_deleted.is_(False))
        if customer_id is not None:
            q = q.filter(Order.customer_id == customer_id)
        if status:
            q = q.filter(Order.status == status)
        return q.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()

    def update(self, order: Order) -> Order:
        self.db.commit()
        self.db.refresh(order)
        return order

    def soft_delete(self, order: Order) -> None:
        order.is_deleted = True
        self.db.commit()
