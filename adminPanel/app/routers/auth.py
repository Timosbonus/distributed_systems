from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, LoginRequest
from app.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    created = service.register(user.username, user.password)

    if not created:
        raise HTTPException(status_code=400, detail="Username exists")

    return UserResponse(id=created.id, username=created.username)


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.login(data.username, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"id": user.id, "username": user.username}