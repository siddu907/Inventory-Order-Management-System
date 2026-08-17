from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(
            Product.id == product_id, Product.is_deleted.is_(False)
        ).first()

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.query(Product).filter(
            Product.sku == sku, Product.is_deleted.is_(False)
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100, category_id: int | None = None,
                min_price: float | None = None, max_price: float | None = None,
                status: str | None = None, search: str | None = None) -> list[Product]:
        from sqlalchemy.orm import joinedload
        
        q = self.db.query(Product).options(joinedload(Product.category)).filter(Product.is_deleted.is_(False))
        if category_id:
            q = q.filter(Product.category_id == category_id)
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)
        if status:
            q = q.filter(Product.status == status)
        if search:
            q = q.filter(
                Product.name.ilike(f"%{search}%") |
                Product.description.ilike(f"%{search}%")
            )
        return q.offset(skip).limit(limit).all()

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def soft_delete(self, product: Product) -> None:
        product.is_deleted = True
        self.db.commit()
