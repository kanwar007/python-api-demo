from pathlib import Path
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import settings
from app.controllers.user_controller import create_user, get_user_service
from app.database import SQLiteDatabase
from app.logging_config import logger
from app.main import app
from app.models.user import UserCreate
from app.repositories.user_repository import SQLiteUserRepository
from app.services.user_service import UserService


@pytest.fixture
def app_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(settings, "auth_username", "test-user")
    monkeypatch.setattr(settings, "auth_password", SecretStr("test-password"))
    monkeypatch.setattr(
        settings,
        "jwt_secret",
        SecretStr("test-jwt-secret-with-at-least-32-characters"),
    )
    database = SQLiteDatabase(str(tmp_path / "api-test.db"))
    repository = SQLiteUserRepository(database)
    service = UserService(repository)
    app.dependency_overrides[get_user_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client(app_client: TestClient) -> TestClient:
    token_response = app_client.post(
        "/api/auth/token",
        headers={
            "AUTH_USERNAME": "test-user",
            "AUTH_PASSWORD": "test-password",
        },
    )
    assert token_response.status_code == 200
    app_client.headers.update(
        {"Authorization": f"Bearer {token_response.json()['access_token']}"}
    )
    return app_client


def test_sqlite_data_persists_after_reopening_database(tmp_path: Path) -> None:
    database_path = str(tmp_path / "users.db")
    first_repository = SQLiteUserRepository(SQLiteDatabase(database_path))

    created_user = first_repository.create(
        UserCreate(name="Ada Lovelace", email="ada@example.com")
    )
    reopened_repository = SQLiteUserRepository(SQLiteDatabase(database_path))

    assert reopened_repository.get_by_id(created_user.id) == created_user


def test_user_controller_creates_user_using_name_field(tmp_path: Path) -> None:
    repository = SQLiteUserRepository(
        SQLiteDatabase(str(tmp_path / "controller-test.db"))
    )
    service = UserService(repository)

    created_user = create_user(
        UserCreate(name="Ada Lovelace", email="ada@example.com"),
        service=service,
    )

    assert created_user.name == "Ada Lovelace"
    assert created_user.id == 1


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


def test_health_check_does_not_require_token(app_client: TestClient) -> None:
    response = app_client.get("/api/health")

    assert response.status_code == 200


def test_user_routes_require_token(app_client: TestClient) -> None:
    response = app_client.get("/api/users/1")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_token_endpoint_rejects_invalid_credentials(app_client: TestClient) -> None:
    response = app_client.post(
        "/api/auth/token",
        headers={
            "AUTH_USERNAME": "test-user",
            "AUTH_PASSWORD": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_token_endpoint_requires_authentication_configuration(
    app_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "auth_username", "")

    response = app_client.post(
        "/api/auth/token",
        headers={
            "AUTH_USERNAME": "test-user",
            "AUTH_PASSWORD": "test-password",
        },
    )

    assert response.status_code == 503


def test_token_endpoint_requires_credential_headers(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/token")

    assert response.status_code == 401


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