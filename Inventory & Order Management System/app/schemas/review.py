from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    product_id: int
    order_id:int
    rating:int = Field(..., ge=1, le=5)
    review: str | None = None


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    review: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    product_id: int
    customer_id: int
    order_id: int
    rating: int
    review: str | None = None
    created_at:datetime
    customer_name: str | None = None
    product_name:str | None = None
