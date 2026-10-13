from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserCreate, UserRead
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService(UserRepository())


def get_user_service() -> UserService:
    return user_service


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return service.create_user(user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user