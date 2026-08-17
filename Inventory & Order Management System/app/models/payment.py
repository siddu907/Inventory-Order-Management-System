from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False, default="Cash")
    payment_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="Pending")
    order = relationship("Order", back_populates="payment", foreign_keys=[order_id])
