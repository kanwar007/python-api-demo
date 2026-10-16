from app.models.user import UserCreate, UserRead
from app.repositories.user_repository import UserRepository
from app.logging_config import logger

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create_user(self, user: UserCreate) -> UserRead:
        logger.info(f"Creating user: {user.name}")
        return self._repository.create(user)

    def get_user(self, user_id: int) -> UserRead | None:
        logger.info(f"Fetching user with ID: {user_id}")
        return self._repository.get_by_id(user_id)