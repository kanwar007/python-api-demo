from app.models.user import UserCreate, UserRead
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create_user(self, user: UserCreate) -> UserRead:
        return self._repository.create(user)

    def get_user(self, user_id: int) -> UserRead | None:
        return self._repository.get_by_id(user_id)