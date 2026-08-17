from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.inventory import Inventory
from app.models.product import Product


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def get_by_product_id(self, product_id: int) -> Inventory | None:
        return (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product))
            .filter(Inventory.product_id == product_id)
            .first()
        )

    def get_by_id(self, inventory_id: int) -> Inventory | None:
        return (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product))
            .filter(Inventory.id == inventory_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Inventory]:
        return (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product))
            .join(Product, Inventory.product_id == Product.id)
            .filter(
                # exclude only explicitly deleted products
                or_(Product.is_deleted.is_(False), Product.is_deleted.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_low_stock(self, skip: int = 0, limit: int = 100) -> list[Inventory]:
        return (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product))
            .join(Product, Inventory.product_id == Product.id)
            .filter(
                or_(Product.is_deleted.is_(False), Product.is_deleted.is_(None)),
                Inventory.current_stock <= Inventory.min_stock_level,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, inventory: Inventory) -> Inventory:
        inventory.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(inventory)
        return inventory
