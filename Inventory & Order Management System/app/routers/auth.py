from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, ChangePassword, ChangePasswordResponse, RefreshTokenRequest, Token, UserLogin, UserRegister
from app.schemas.user import UserOut, UserOutNoImage, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserOutNoImage, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    return AuthService(db).register(user_in)


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user, access_token, refresh_token = AuthService(db).login(credentials)
    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer", "user": user}


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token = service.refresh_access_token(payload.refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserOut)
def profile(request: Request, current_user: User = Depends(get_current_user)):
    # Convert profile_image path to full URL
    if current_user.profile_image:
        path_part = "/uploads/files" + current_user.profile_image[len("/uploads"):]
        encoded = quote(path_part, safe="/")
        current_user.profile_image = f"{str(request.base_url).rstrip('/')}{encoded}"
    return current_user


@router.put("/profile", response_model=UserOutNoImage)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    updated = False

    if payload.email is not None:
        existing = repo.get_by_email(payload.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email is already registered")
        current_user.email = payload.email
        updated = True

    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
        updated = True

    if payload.phone is not None:
        existing = repo.get_by_phone(payload.phone)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Phone number already registered")
        current_user.phone = payload.phone
        updated = True

    if payload.address is not None:
        current_user.address = payload.address.strip()
        updated = True

    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No valid profile fields provided to update")

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put(
    "/change-password",
    response_model=ChangePasswordResponse,
    description=(
        "Change your password. Requirements:\n\n"
        "- At least 8 characters\n"
        "- At least one uppercase letter\n"
        "- At least one lowercase letter\n"
        "- At least one digit\n"
        "- At least one special character"
    ),
)
def change_password(
    payload: ChangePassword = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).change_password(current_user, payload.new_password)
    return {"message": "Password changed successfully"}
