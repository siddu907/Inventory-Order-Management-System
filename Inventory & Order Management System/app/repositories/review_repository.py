from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_product(self, product_id: int,
                       skip: int = 0, limit: int = 100) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.product_id == product_id)
            .offset(skip).limit(limit).all()
        )

    def exists(self, customer_id: int, product_id: int, order_id: int) -> bool:
        return (
            self.db.query(Review)
            .filter(
                Review.customer_id == customer_id,
                Review.product_id == product_id,
                Review.order_id == order_id,
            )
            .first() is not None
        )

    def average_rating(self, product_id: int) -> float:
        reviews = self.db.query(Review).filter(Review.product_id == product_id).all()
        if not reviews:
            return 0.0
        return sum(r.rating for r in reviews) / len(reviews)

    def update(self, review: Review) -> Review:
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()
