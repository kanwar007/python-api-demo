from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.controllers.user_controller import get_user_service
from app.logging_config import logger
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.fixture
def client() -> TestClient:
    service = UserService(UserRepository())
    app.dependency_overrides[get_user_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_and_get_user(client: TestClient) -> None:
    create_response = client.post(
        "/users",
        json={"name": "Ada Lovelace", "email": "ada@example.com"},
    )

    assert create_response.status_code == 201
    user = create_response.json()
    assert user == {
        "id": 1,
        "name": "Ada Lovelace",
        "email": "ada@example.com",
    }

    get_response = client.get("/users/1")

    assert get_response.status_code == 200
    assert get_response.json() == user


def test_get_missing_user_returns_404(client: TestClient) -> None:
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_application_uses_environment_settings(client: TestClient) -> None:
    assert app.title == settings.app_name
    assert app.debug == settings.debug
    assert app.state.settings.app_env == settings.app_env


def test_requests_are_written_to_log_file(client: TestClient) -> None:
    response = client.get("/health")
    for handler in logger.handlers:
        handler.flush()

    assert response.status_code == 200
    assert "GET /health -> 200" in Path(settings.log_file).read_text(encoding="utf-8")