from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.product import Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.cache_service import CacheService


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.cache = CacheService() if settings.redis_enabled else None

    def create(self, payload: ProductCreate) -> Product:
        # validate category exists
        cat = CategoryRepository(self.db).get_by_id(payload.category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
        # validate unique SKU
        if self.repo.get_by_sku(payload.sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="A product with this SKU already exists")

        product = self.repo.create(Product(**payload.model_dump()))
        
        return product

    def get_all(self, skip: int = 0, limit: int = 100, category_id: int | None = None,
                min_price: float | None = None, max_price: float | None = None,
                status: str | None = None, search: str | None = None):
        
        return self.repo.get_all(skip=skip, limit=limit, category_id=category_id,min_price=min_price, max_price=max_price,status=status, search=search)

    def get_by_id(self, product_id: int) -> Product:
        # Try cache first
        if self.cache:
            cache_key = f"product:{product_id}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                # Return cached product if found in DB (in case it was deleted)
                product = self.repo.get_by_id(product_id)
                if product:
                    return product
        
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
        
        # Cache the result
        if self.cache:
            self.cache.set(f"product:{product_id}", True, ttl=settings.cache_ttl)
        
        return product

    def update(self, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get_by_id(product_id)
        updates = payload.model_dump(exclude_unset=True)
        if "category_id" in updates:
            cat = CategoryRepository(self.db).get_by_id(updates["category_id"])
            if not cat:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
        if "sku" in updates and updates["sku"] != product.sku:
            existing = self.repo.get_by_sku(updates["sku"])
            if existing and existing.id != product_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="A product with this SKU already exists")

        # if stock_quantity is being updated directly, sync inventory too
        if "stock_quantity" in updates:
            inv_repo = InventoryRepository(self.db)
            inv = inv_repo.get_by_product_id(product_id)
            if inv:
                inv.current_stock = updates["stock_quantity"]
                inv_repo.update(inv)

        for key, val in updates.items():
            setattr(product, key, val)
        
        updated_product = self.repo.update(product)
        
        # Invalidate cache
        if self.cache:
            self.cache.delete(f"product:{product_id}")
        
        return updated_product

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.repo.soft_delete(product)
        
        # Invalidate cache
        if self.cache:
            self.cache.delete(f"product:{product_id}")
