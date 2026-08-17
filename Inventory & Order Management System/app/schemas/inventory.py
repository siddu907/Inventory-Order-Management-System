from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int = Field(..., ge=0)
    min_stock_level: int = Field(0, ge=0)
    max_stock_level: int = Field(100, ge=1)


class InventoryUpdate(BaseModel):
    current_stock:   int | None = Field(None, ge=0, description="Directly set the current stock count")
    min_stock_level: int | None = Field(None, ge=0)
    max_stock_level: int | None = Field(None, ge=1)


class StockAdjust(BaseModel):
    quantity: int = Field(..., gt=0, description="Number of units to add or remove")


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    current_stock: int
    min_stock_level:int
    max_stock_level:int
    last_updated:datetime | None = None

    # denormalized from product
    product_name:str | None = None
    product_sku: str | None = None
    product_status:str | None = None
