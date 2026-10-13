import pytest
from fastapi.testclient import TestClient

from app.controllers.user_controller import get_user_service
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