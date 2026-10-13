from app.models.user import UserCreate, UserRead


class UserRepository:
    def __init__(self) -> None:
        self._users: dict[int, UserRead] = {}
        self._next_id = 1

    def create(self, user: UserCreate) -> UserRead:
        saved_user = UserRead(id=self._next_id, **user.model_dump())
        self._users[saved_user.id] = saved_user
        self._next_id += 1
        return saved_user

    def get_by_id(self, user_id: int) -> UserRead | None:
        return self._users.get(user_id)