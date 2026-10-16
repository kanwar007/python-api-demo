from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service
from app.models.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.logging_config import logger

router = APIRouter(prefix="/users", tags=["users"])
logger.info("User controller initialized")


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    logger.info("Creating user: %s", user.name)
    return service.create_user(user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    logger.info(f"Fetching user with ID: {user_id}")
    user = service.get_user(user_id)
    if user is None:
        logger.warning(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User found with ID: {user_id}")
    return user