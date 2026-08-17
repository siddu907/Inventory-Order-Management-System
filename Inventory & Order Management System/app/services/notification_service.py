from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)

    def create(self, user_id: int, title: str, message: str,
               order_id: int | None = None,
               payment_id: int | None = None,
               notification_type: str | None = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            order_id=order_id,
            payment_id=payment_id,
            notification_type=notification_type,
            created_at=datetime.utcnow(),
        )
        return self.repo.create(notification)

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.repo.get_for_user(user_id, skip=skip, limit=limit)

    def mark_read(self, notification_id: int, user_id: int) -> Notification:
        notification = self.repo.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Notification not found")
        return self.repo.mark_read(notification)
