from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message= Column(Text, nullable=False)
    is_read= Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    notification_type = Column(String(50), nullable=True)
    user = relationship("User", foreign_keys=[user_id])
