from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.oauth2 import get_current_user
from app.core.permissions import require_roles
from app.database import get_db
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.upload_service import UploadService

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}


def _validate_image(file: UploadFile) -> None:
    if not file.filename or not file.filename.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Uploaded file must have a filename")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unsupported image type. Allowed: jpg, jpeg, png, webp")
    try:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to validate uploaded image")
    if size > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File too large. Max allowed: {settings.max_upload_size} bytes")


def _make_url(request: Request, path: str) -> str:
    path_part = "/uploads/files" + path[len("/uploads"):]
    encoded = quote(path_part, safe="/")
    return f"{str(request.base_url).rstrip('/')}{encoded}"


@router.post("/profile-image", status_code=status.HTTP_200_OK)
def upload_profile_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Any authenticated user can upload their own profile image."""
    _validate_image(file)
    svc = UploadService(settings.upload_dir)
    try:
        path = svc.save_upload(file, "profile_images")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save profile image") from exc
    current_user.profile_image = path
    db.commit()
    return {"message": "Profile image uploaded successfully",
            "path": path, "url": _make_url(request, path)}


@router.post("/product-image/{product_id}", status_code=status.HTTP_200_OK)
def upload_product_image(
    product_id: int,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin or Staff can upload a product image."""
    require_roles(current_user, {"Admin", "Staff"})
    _validate_image(file)
    product = ProductRepository(db).get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")
    svc = UploadService(settings.upload_dir)
    try:
        path = svc.save_upload(file, "product_images")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save product image") from exc
    product.product_image = path
    db.commit()
    return {"message": "Product image uploaded successfully",
            "path": path, "url": _make_url(request, path)}
