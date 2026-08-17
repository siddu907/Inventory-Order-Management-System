from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.cache_service import CacheService
from app.services.product_service import ProductService
from app.utils.helpers import uploads_path_to_url

router = APIRouter()


def _enrich(product_out: dict, request: Request | None) -> dict:
    if request and product_out.get("product_image"):
        product_out["product_image"] = uploads_path_to_url(
            str(request.base_url), product_out["product_image"]
        )
    return product_out


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    require_roles(current_user, {"Admin", "Staff"})
    product = ProductService(db).create(payload)
    
    # Invalidate list cache
    try:
        CacheService().clear_namespace("products:list:")
        print("Invalidated products list cache after create")
    except Exception as e:
        print(f"Cache invalidation failed: {e}")
    
    out = ProductOut.model_validate(product).model_dump()
    return _enrich(out, request)


@router.get("", response_model=list[ProductOut])
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    request: Request = None,
):
    try:
        # Cache implementation
        cache = CacheService()
        cache_key = f"products:list:{skip}:{limit}:{category_id}:{min_price}:{max_price}:{status}:{search}"
        
        # Try to get from cache
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"Cache HIT for key: {cache_key}")
            # Apply URL enrichment to cached data
            if request:
                cached = [_enrich(product, request) for product in cached]
            return cached
        
        print(f"Cache MISS for key: {cache_key}")
        
        # Get products from service
        products = ProductService(db).get_all(
            skip=skip, limit=limit, category_id=category_id,
            min_price=min_price, max_price=max_price,
            status=status, search=search,
        )
        
        # Convert to Pydantic models then to dict for JSON serialization
        result = [ProductOut.model_validate(p).model_dump() for p in products]
        
        # Cache the serialized result (without URLs to avoid caching absolute URLs)
        cache.set(cache_key, result, ttl=settings.cache_ttl)
        print(f"Cached {len(result)} products with key: {cache_key}")
        
        # Apply URL enrichment before returning
        if request:
            result = [_enrich(product, request) for product in result]
        
        return result
        
    except Exception as e:
        # Log the actual error
        print(f"ERROR in list_products: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise e


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), request: Request = None):
    product = ProductService(db).get_by_id(product_id)
    out = ProductOut.model_validate(product).model_dump()
    return _enrich(out, request)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    require_roles(current_user, {"Admin", "Staff"})
    product = ProductService(db).update(product_id, payload)
    
    # Invalidate list cache
    try:
        CacheService().clear_namespace("products:list:")
        print("Invalidated products list cache after update")
    except Exception as e:
        print(f"Cache invalidation failed: {e}")
    
    out = ProductOut.model_validate(product).model_dump()
    return _enrich(out, request)


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_roles(current_user, {"Admin", "Staff"})
    ProductService(db).delete(product_id)
    
    # Invalidate list cache
    try:
        CacheService().clear_namespace("products:list:")
        print("Invalidated products list cache after delete")
    except Exception as e:
        print(f"Cache invalidation failed: {e}")
    
    return {"message": "Product deleted successfully"}
