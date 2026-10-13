import sqlite3
from contextlib import closing
from pathlib import Path

from app.models.user import UserCreate, UserRead


class SQLiteDatabase:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def create_user(self, user: UserCreate) -> UserRead:
        with closing(sqlite3.connect(self._database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (user.name, user.email),
                )
                row = connection.execute(
                    "SELECT id, name, email FROM users WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()

        if row is None:
            raise RuntimeError("Created user could not be read from SQLite")
        return UserRead(id=row[0], name=row[1], email=row[2])

    def get_user(self, user_id: int) -> UserRead | None:
        with closing(sqlite3.connect(self._database_path)) as connection:
            row = connection.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        if row is None:
            return None
        return UserRead(id=row[0], name=row[1], email=row[2])

    def _initialize(self) -> None:
        with closing(sqlite3.connect(self._database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                    """
                )