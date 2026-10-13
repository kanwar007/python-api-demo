from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.controllers.user_controller import get_user_service
from app.database import SQLiteDatabase
from app.logging_config import logger
from app.main import app
from app.models.user import UserCreate
from app.repositories.user_repository import SQLiteUserRepository
from app.services.user_service import UserService


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    database = SQLiteDatabase(str(tmp_path / "api-test.db"))
    repository = SQLiteUserRepository(database)
    service = UserService(repository)
    app.dependency_overrides[get_user_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_sqlite_data_persists_after_reopening_database(tmp_path: Path) -> None:
    database_path = str(tmp_path / "users.db")
    first_repository = SQLiteUserRepository(SQLiteDatabase(database_path))

    created_user = first_repository.create(
        UserCreate(name="Ada Lovelace", email="ada@example.com")
    )
    reopened_repository = SQLiteUserRepository(SQLiteDatabase(database_path))

    assert reopened_repository.get_by_id(created_user.id) == created_user


def test_create_and_get_user(client: TestClient) -> None:
    create_response = client.post(
        "/api/users",
        json={"name": "Ada Lovelace", "email": "ada@example.com"},
    )

    assert create_response.status_code == 201
    user = create_response.json()
    assert user == {
        "id": 1,
        "name": "Ada Lovelace",
        "email": "ada@example.com",
    }

    get_response = client.get("/api/users/1")

    assert get_response.status_code == 200
    assert get_response.json() == user


def test_get_missing_user_returns_404(client: TestClient) -> None:
    response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_application_uses_environment_settings(client: TestClient) -> None:
    assert app.title == settings.app_name
    assert app.debug == settings.debug
    assert app.state.settings.app_env == settings.app_env


def test_requests_are_written_to_log_file(client: TestClient) -> None:
    response = client.get("/api/health")
    for handler in logger.handlers:
        handler.flush()

    assert response.status_code == 200
    assert "GET /api/health -> 200" in Path(settings.log_file).read_text(encoding="utf-8")