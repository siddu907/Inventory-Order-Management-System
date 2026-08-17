from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.cache_service import CacheService
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin"})
    category = CategoryService(db).create(payload)
    
    # Invalidate list cache
    try:
        CacheService().clear_namespace("categories:list:")
        print("Invalidated categories list cache after create")
    except Exception as e:
        print(f"Cache invalidation failed: {e}")
    
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(
    search: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        # Cache implementation
        cache = CacheService()
        cache_key = f"categories:list:{skip}:{limit}:{status}:{search}"
        
        # Try to get from cache
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"Cache HIT for key: {cache_key}")
            return cached
        
        print(f"Cache MISS for key: {cache_key}")
        
        # Get categories from service
        categories = CategoryService(db).get_all(skip=skip, limit=limit,
                                                  status_filter=status, search=search)
        
        # Convert to Pydantic models then to dict for JSON serialization
        result = [CategoryOut.model_validate(c).model_dump() for c in categories]
        
        # Cache the serialized result
        cache.set(cache_key, result, ttl=settings.cache_ttl)
        print(f"Cached {len(result)} categories with key: {cache_key}")
        
        # Return the result (FastAPI will handle the response model conversion)
        return result
        
    except Exception as e:
        # Log the actual error
        print(f"ERROR in list_categories: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise e


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService(db).get_by_id(category_id)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin"})
    category = CategoryService(db).update(category_id, payload)
    
    # Invalidate list cache
    CacheService().clear_namespace("categories:list:")
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin"})
    CategoryService(db).delete(category_id)
    
    # Invalidate list cache
    CacheService().clear_namespace("categories:list:")
    
    return {"message": "Category deleted successfully"}
