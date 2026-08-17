from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="Active")
    product_image = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at= Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("Category", back_populates="products", foreign_keys=[category_id])
    inventory = relationship("Inventory", back_populates="product", uselist=False, primaryjoin="Product.id==Inventory.product_id")
    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None
