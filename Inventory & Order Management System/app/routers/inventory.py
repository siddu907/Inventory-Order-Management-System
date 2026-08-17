from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryOut, InventoryUpdate, StockAdjust
from app.services.inventory_service import InventoryService
from app.background.notification_tasks import notify_low_stock

router = APIRouter()


def _to_out(inv: Inventory) -> InventoryOut:
    """Convert ORM Inventory object to InventoryOut schema."""
    product = inv.product
    return InventoryOut(
        id=inv.id,
        product_id=inv.product_id,
        current_stock=inv.current_stock,
        min_stock_level=inv.min_stock_level,
        max_stock_level=inv.max_stock_level,
        last_updated=inv.last_updated,
        product_name=product.name if product else None,
        product_sku=product.sku if product else None,
        product_status=product.status if product else None,
    )


def _fetch_inv(product_id: int, db: Session) -> Inventory | None:
    """Fetch inventory with product eagerly loaded."""
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .filter(Inventory.product_id == product_id)
        .first()
    )


def _notify_low_stock(inv: Inventory, bg: BackgroundTasks) -> None:
    """Trigger low stock notification with both in-app and email alerts."""
    if inv.current_stock <= inv.min_stock_level and inv.product:
        # Use the proper notify_low_stock function that sends both in-app and email notifications
        bg.add_task(
            notify_low_stock,
            product_id=inv.product_id,
            product_name=inv.product.name,
            product_sku=inv.product.sku,
            current_stock=inv.current_stock,
            min_stock=inv.min_stock_level
        )


@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_inventory(
    payload: InventoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    inv = InventoryService(db).create(payload)
    inv = _fetch_inv(inv.product_id, db)
    return _to_out(inv)


@router.get("", response_model=list[InventoryOut])
def list_inventory(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    # Query inventory with eagerly loaded product, only non-deleted products
    records = (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .join(Product, Inventory.product_id == Product.id)
        .filter(or_(Product.is_deleted.is_(False), Product.is_deleted.is_(None)))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_out(i) for i in records]


@router.get("/low-stock", response_model=list[InventoryOut])
def list_low_stock(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    records = (
        db.query(Inventory)
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
    return [_to_out(i) for i in records]


@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    inv = _fetch_inv(product_id, db)
    if not inv:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inventory record not found for this product")
    return _to_out(inv)


@router.put("/{product_id}", response_model=InventoryOut)
def update_inventory(
    product_id: int,
    payload: InventoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    InventoryService(db).update(product_id, payload)
    inv = _fetch_inv(product_id, db)
    return _to_out(inv)


@router.post("/{product_id}/add-stock", response_model=InventoryOut)
def add_stock(
    product_id: int,
    payload: StockAdjust,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    InventoryService(db).add_stock(product_id, payload.quantity)
    inv = _fetch_inv(product_id, db)
    _notify_low_stock(inv, background_tasks)
    return _to_out(inv)


@router.post("/{product_id}/remove-stock", response_model=InventoryOut)
def remove_stock(
    product_id: int,
    payload: StockAdjust,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    InventoryService(db).remove_stock(product_id, payload.quantity)
    inv = _fetch_inv(product_id, db)
    _notify_low_stock(inv, background_tasks)
    return _to_out(inv)
