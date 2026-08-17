from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    status: str = "Active"

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        allowed = {"Active", "Inactive"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    status: str | None = None

    @field_validator("status")
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in {"Active", "Inactive"}:
            raise ValueError("Status must be Active or Inactive")
        return v


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime | None = None
