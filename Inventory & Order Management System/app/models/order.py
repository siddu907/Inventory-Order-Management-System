from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_amount= Column(Float, nullable=False, default=0.0)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), nullable=False, default="Pending")
    is_deleted = Column(Boolean, default=False)
    
    # Coupon fields
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=True)
    coupon_code = Column(String, nullable=True)
    discount_amount = Column(Float, nullable=False, default=0.0)

    customer= relationship("User", foreign_keys=[customer_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)
    coupon = relationship("Coupon", back_populates="orders")

    @property
    def customer_name(self) -> str | None:
        return self.customer.full_name if self.customer else None


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id= Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product= relationship("Product", foreign_keys=[product_id])
    @property
    def product_name(self) -> str | None:
        return self.product.name if self.product else None
