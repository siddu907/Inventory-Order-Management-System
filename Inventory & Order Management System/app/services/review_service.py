from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReviewRepository(db)

    def create_review(self, customer_id: int, payload: ReviewCreate) -> Review:
        # check order belongs to customer and is Delivered
        order = self.db.query(Order).filter(
            Order.id == payload.order_id,
            Order.customer_id == customer_id,
            Order.is_deleted.is_(False),
        ).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.status != "Delivered":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You can only review products from delivered orders")

        # check product was in that order
        item = self.db.query(OrderItem).filter(
            OrderItem.order_id == payload.order_id,
            OrderItem.product_id == payload.product_id,
        ).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Product was not part of this order")

        # prevent duplicate review
        if self.repo.exists(customer_id, payload.product_id, payload.order_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You have already reviewed this product for this order")

        review = Review(
            product_id=payload.product_id,
            customer_id=customer_id,
            order_id=payload.order_id,
            rating=payload.rating,
            review=payload.review,
        )
        return self.repo.create(review)

    def get_product_reviews(self, product_id: int,skip: int = 0, limit: int = 100) -> list[Review]:
        return self.repo.get_by_product(product_id, skip=skip, limit=limit)

    def update_review(self, review_id: int,customer_id: int, payload: ReviewUpdate) -> Review:
        review = self.repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
        if review.customer_id != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        updates = payload.model_dump(exclude_unset=True)
        for key, val in updates.items():
            setattr(review, key, val)
        return self.repo.update(review)

    def delete_review(self, review_id: int, customer_id: int) -> None:
        review = self.repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
        if review.customer_id != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,  detail="Not allowed")
        self.repo.delete(review)

    def average_rating(self, product_id: int) -> float:
        return self.repo.average_rating(product_id)
