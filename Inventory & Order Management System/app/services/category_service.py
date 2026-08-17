from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.cache_service import CacheService


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)
        self.cache = CacheService() if settings.redis_enabled else None

    def create(self, payload: CategoryCreate) -> Category:
        if self.repo.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category with this name already exists")
        category = self.repo.create(Category(**payload.model_dump()))
        
        return category

    def get_all(self, skip: int = 0, limit: int = 100,
                status_filter: str | None = None, search: str | None = None):
        # For list endpoints, we don't cache at service level due to SQLAlchemy object complexity
        # Caching would need to be implemented at router level after serialization
        # Individual categories are cached in get_by_id()
        return self.repo.get_all(skip=skip, limit=limit, status=status_filter, search=search)

    def get_by_id(self, category_id: int) -> Category:
        # Try cache first
        if self.cache:
            cache_key = f"category:{category_id}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                cat = self.repo.get_by_id(category_id)
                if cat:
                    return cat
        
        cat = self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
        # Cache the result
        if self.cache:
            self.cache.set(f"category:{category_id}", True, ttl=settings.cache_ttl)
        
        return cat

    def update(self, category_id: int, payload: CategoryUpdate) -> Category:
        cat = self.get_by_id(category_id)
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates and updates["name"] != cat.name:
            if self.repo.get_by_name(updates["name"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this name already exists")
        for key, val in updates.items():
            setattr(cat, key, val)
        
        updated_cat = self.repo.update(cat)
        
        # Invalidate cache
        if self.cache:
            self.cache.delete(f"category:{category_id}")
        
        return updated_cat

    def delete(self, category_id: int) -> None:
        cat = self.get_by_id(category_id)
        self.repo.soft_delete(cat)
        
        # Invalidate cache
        if self.cache:
            self.cache.delete(f"category:{category_id}")
