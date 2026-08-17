from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str = Field("Cash", description="Cash, Card, UPI, or Online")

    @field_validator("payment_method")
    def validate_method(cls, v: str) -> str:
        allowed = {"Cash", "Card", "UPI", "Online"}
        if v not in allowed:
            raise ValueError(f"payment_method must be one of {allowed}")
        return v


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    order_id:       int
    amount:         float
    payment_method: str
    payment_date:   datetime | None = None
    status:         str
