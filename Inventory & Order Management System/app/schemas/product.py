from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category_id: int
    price: float = Field(..., gt=0)
    sku: str = Field(..., min_length=1, max_length=100)
    stock_quantity: int = Field(..., ge=0)
    status: str = "Active"

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        if v not in {"Active", "Inactive"}:
            raise ValueError("Status must be Active or Inactive")
        return v


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    price: float | None = Field(None, gt=0)
    sku: str | None = Field(None, min_length=1)
    stock_quantity: int | None = Field(None, ge=0)
    status: str | None = None

    @field_validator("status")
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in {"Active", "Inactive"}:
            raise ValueError("Status must be Active or Inactive")
        return v


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    category_id: int
    category_name: str | None = None
    price: float
    sku: str
    stock_quantity: int
    status: str
    product_image: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
