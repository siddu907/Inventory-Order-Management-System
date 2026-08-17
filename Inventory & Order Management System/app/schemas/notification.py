from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict, Field


# Base notification with common fields
class NotificationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime | None = None
    notification_type: str


# Order notifications (order_created, order_confirmed, order_shipped, order_delivered, order_cancelled)
class OrderNotification(NotificationBase):
    order_id: int | None = None


# Payment notifications (payment_completed, payment_refunded)
class PaymentNotification(NotificationBase):
    order_id: int | None = None
    payment_id: int | None = None


# Low stock notifications (low_stock)
class LowStockNotification(NotificationBase):
    pass


# Union type for API responses
NotificationResponse = Union[OrderNotification, PaymentNotification, LowStockNotification]


# Legacy schema for backward compatibility (if needed elsewhere)
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime | None = None
    order_id: int | None = None
    payment_id: int | None = None
    notification_type: str | None = None
