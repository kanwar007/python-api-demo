from app.config import settings
from app.database import SQLiteDatabase
from app.repositories.user_repository import SQLiteUserRepository, UserRepository
from app.services.user_service import UserService

database = SQLiteDatabase(settings.database_path)
user_repository: UserRepository = SQLiteUserRepository(database)
user_service = UserService(user_repository)


def get_user_service() -> UserService:
    return user_service