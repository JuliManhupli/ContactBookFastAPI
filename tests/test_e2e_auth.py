from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.conf import messages
from src.entity.models import User
from tests.conftest import TestingSessionLocal

user_data = {"username": "geralt", "email": "geralt_of_rivia@gmail.com", "password": "1234567"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    assert response.json() == {"detail": messages.ACCOUNT_EXISTS}


def test_not_confirmed_login(client):
    response = client.post("api/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": messages.NOT_CONFIRMED}


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data["email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_invalid_email_login(client):
    response = client.post("api/auth/login",
                           data={"username": "email", "password": user_data["password"]})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": messages.INVALID_EMAIL}


def test_invalid_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data["email"], "password": "password"})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": messages.INVALID_PASSWORD}


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": "password"})
    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_repeat_request_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/request_email", json={"email": user_data["email"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.EMAIL_CONFIRMED_ERROR


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data["email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = False
            await session.commit()

    response = client.post("api/auth/request_email", json={"email": user_data["email"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == messages.CHECK_EMAIL
    mock_send_email.assert_called_once()
