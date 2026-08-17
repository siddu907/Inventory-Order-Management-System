from datetime import datetime
from urllib.parse import quote


def now() -> datetime:
    return datetime.utcnow()


def uploads_path_to_url(base_url: str, internal_path: str) -> str | None:
    """Convert an internal storage path like '/uploads/product_images/img.jpg'
    to a publicly accessible URL served from the '/uploads/files' static mount."""
    if not internal_path:
        return None
    if not internal_path.startswith("/uploads"):
        return internal_path
    path_part = "/uploads/files" + internal_path[len("/uploads"):]
    encoded   = quote(path_part, safe="/")
    return f"{base_url.rstrip('/')}{encoded}"
