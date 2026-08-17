from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(
            Category.id == category_id, Category.is_deleted.is_(False)
        ).first()

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(
            Category.name == name, Category.is_deleted.is_(False)
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100,
                status: str | None = None, search: str | None = None) -> list[Category]:
        q = self.db.query(Category).filter(Category.is_deleted.is_(False))
        if status:
            q = q.filter(Category.status == status)
        if search:
            q = q.filter(Category.name.ilike(f"%{search}%"))
        return q.offset(skip).limit(limit).all()

    def update(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category

    def soft_delete(self, category: Category) -> None:
        category.is_deleted = True
        self.db.commit()
