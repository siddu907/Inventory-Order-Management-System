from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("product_id", "customer_id", "order_id", name="uq_review_product_customer_order"),)

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    review  = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    product  = relationship("Product", foreign_keys=[product_id])
    customer = relationship("User",    foreign_keys=[customer_id])
    order = relationship("Order",   foreign_keys=[order_id])
