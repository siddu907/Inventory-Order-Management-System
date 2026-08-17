from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationOut, OrderNotification, PaymentNotification, LowStockNotification
from app.services.notification_service import NotificationService

router = APIRouter()


def _format_notification(notification) -> dict[str, Any]:
    """Format notification based on its type, excluding irrelevant fields."""
    base_data = {
        "id": notification.id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "notification_type": notification.notification_type or "unknown",
    }
    
    # Determine notification category based on notification_type
    notif_type = (notification.notification_type or "").lower()
    
    if "payment" in notif_type:
        # Payment notifications: include both order_id and payment_id
        return PaymentNotification(
            **base_data,
            order_id=notification.order_id,
            payment_id=notification.payment_id
        ).model_dump(exclude_none=True)
    elif "order" in notif_type:
        # Order notifications: include only order_id
        return OrderNotification(
            **base_data,
            order_id=notification.order_id
        ).model_dump(exclude_none=True)
    else:
        # Low stock or other notifications: no order_id or payment_id
        return LowStockNotification(**base_data).model_dump(exclude_none=True)


@router.get("")
def list_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of notifications with type-specific formatting."""
    notifications = NotificationService(db).list_for_user(current_user.id, skip=skip, limit=limit)
    return [_format_notification(n) for n in notifications]


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read and return it with type-specific formatting."""
    notification = NotificationService(db).mark_read(notification_id, current_user.id)
    return _format_notification(notification)
