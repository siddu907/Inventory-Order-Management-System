from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1)
    coupon_code: str | None = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id:int
    product_name: str | None = None
    quantity:int
    unit_price:float
    subtotal: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    customer_id: int
    customer_name: str | None = None
    total_amount:float
    order_date: datetime
    status: str
    items: list[OrderItemOut] = []
    coupon_code: str | None = None
    discount_amount: float = 0.0
