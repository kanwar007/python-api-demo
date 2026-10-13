from typing import Protocol

from app.database import SQLiteDatabase
from app.models.user import UserCreate, UserRead


class UserRepository(Protocol):
    def create(self, user: UserCreate) -> UserRead: ...

    def get_by_id(self, user_id: int) -> UserRead | None: ...


class SQLiteUserRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def create(self, user: UserCreate) -> UserRead:
        return self._database.create_user(user)

    def get_by_id(self, user_id: int) -> UserRead | None:
        return self._database.get_user(user_id)