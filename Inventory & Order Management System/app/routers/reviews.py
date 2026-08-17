from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate
from app.services.review_service import ReviewService

router = APIRouter()


def _to_out(r) -> ReviewOut:
    return ReviewOut(
        id=r.id,
        product_id=r.product_id,
        customer_id=r.customer_id,
        order_id=r.order_id,
        rating=r.rating,
        review=r.review,
        created_at=r.created_at,
        customer_name=r.customer.full_name if r.customer else None,
        product_name=r.product.name if r.product else None,
    )


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Customer"})
    r = ReviewService(db).create_review(current_user.id, payload)
    return _to_out(r)


@router.get("/product/{product_id}", response_model=list[ReviewOut])
def list_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    reviews = ReviewService(db).get_product_reviews(product_id, skip=skip, limit=limit)
    return [_to_out(r) for r in reviews]


@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Customer"})
    r = ReviewService(db).update_review(review_id, current_user.id, payload)
    return _to_out(r)


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Customer"})
    ReviewService(db).delete_review(review_id, current_user.id)
    return {"message": "Review deleted successfully"}
