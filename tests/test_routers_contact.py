from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def user_create_body():
    return {
        "email": "test@example.com",
        "passwd": "strongpassword123",
    }


@pytest.fixture
def user_find():
    return {
        "email": "test@example.com",
        "passwd": "strongpassword123",
        "is_active": False,
        "salt": "test",
        "otp": "123456",
        "created_at": "2021-01-01 00:00:00",
        "updated_at": "2021-01-01 00:00:00",
    }


@pytest.fixture
def mock_auth(monkeypatch):
    monkeypatch.setattr("routers.auth.oauth2_scheme", AsyncMock(return_value="fake_token"))
    mock_get_current_user = AsyncMock(return_value=user)
    monkeypatch.setattr("service.auth.get_current_user", mock_get_current_user)


@pytest.fixture
def mock_db_session(monkeypatch):
    async_mock_db_session = AsyncMock()
    monkeypatch.setattr("conf.db.get_db", async_mock_db_session)


@pytest.fixture
def mock_rate_limit(monkeypatch):
    async_mock_rate_limit = AsyncMock()
    monkeypatch.setattr("service.rate_limiter.limit_allowed", async_mock_rate_limit)


@pytest.fixture
def mock_auth_create_user(monkeypatch, user_find):
    async_mock = AsyncMock(return_value=user_find)
    monkeypatch.setattr("service.auth.create_user", async_mock)


def test_signup(client, user_create_body, mock_db_session, mock_rate_limit, mock_auth_create_user):
    response = client.post("/auth/signup", json=user_create_body)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user_create_body["email"]
    assert data["passwd"] == user_create_body["passwd"]
    assert data["is_active"] is False
