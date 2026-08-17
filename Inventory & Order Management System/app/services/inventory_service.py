from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def _validate_stock_levels(current_stock: int, min_stock_level: int,
                            max_stock_level: int) -> None:
    """Validate stock level constraints and raise descriptive errors."""
    if current_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="current_stock cannot be negative.",
        )
    if min_stock_level >= max_stock_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"min_stock_level ({min_stock_level}) must be less than "
                   f"max_stock_level ({max_stock_level}).",
        )
    if current_stock > max_stock_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"current_stock cannot be greater than "
                   f"max_stock_level ({max_stock_level}).",
        )


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def create(self, payload: InventoryCreate) -> Inventory:
        product = ProductRepository(self.db).get_by_id(payload.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Product not found")

        if self.repo.get_by_product_id(payload.product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory record already exists for this product. ",
            )

        # validate stock levels
        _validate_stock_levels(payload.current_stock,
                               payload.min_stock_level,
                               payload.max_stock_level)

        inv = Inventory(
            product_id=payload.product_id,
            current_stock=payload.current_stock,
            min_stock_level=payload.min_stock_level,
            max_stock_level=payload.max_stock_level,
        )
        product.stock_quantity = payload.current_stock
        self.db.commit()
        return self.repo.create(inv)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def get_low_stock(self, skip: int = 0, limit: int = 100):
        return self.repo.get_low_stock(skip=skip, limit=limit)

    def get_by_product_id(self, product_id: int) -> Inventory:
        inv = self.repo.get_by_product_id(product_id)
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Inventory record not found for this product")
        return inv

    def update(self, product_id: int, payload: InventoryUpdate) -> Inventory:
        inv = self.get_by_product_id(product_id)
        updates = payload.model_dump(exclude_unset=True)

        # resolve final values after update
        final_current = updates.get("current_stock",   inv.current_stock)
        final_min     = updates.get("min_stock_level", inv.min_stock_level)
        final_max     = updates.get("max_stock_level", inv.max_stock_level)

        # validate all three together
        _validate_stock_levels(final_current, final_min, final_max)

        for key, val in updates.items():
            setattr(inv, key, val)

        # sync product.stock_quantity if current_stock changed
        if "current_stock" in updates:
            inv.product.stock_quantity = updates["current_stock"]

        return self.repo.update(inv)

    def add_stock(self, product_id: int, quantity: int) -> Inventory:
        inv = self.get_by_product_id(product_id)
        new_stock = inv.current_stock + quantity

        if new_stock > inv.max_stock_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add stock: result ({new_stock}) would exceed "
                       f"max_stock_level ({inv.max_stock_level}).",
            )

        inv.current_stock = new_stock
        inv.product.stock_quantity = new_stock
        return self.repo.update(inv)

    def remove_stock(self, product_id: int, quantity: int) -> Inventory:
        inv = self.get_by_product_id(product_id)
        new_stock = inv.current_stock - quantity

        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove stock: result ({new_stock}) would be negative. "
                       f"Available stock: {inv.current_stock}.",
            )

        inv.current_stock = new_stock
        inv.product.stock_quantity = new_stock
        return self.repo.update(inv)

    def _check_low_stock(self, inv: Inventory) -> bool:
        return inv.current_stock <= inv.min_stock_level
