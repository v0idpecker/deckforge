import uuid
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import allure
import pytest
from authlib.integrations.base_client.errors import OAuthError
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from deckforge.adapters.errors import ExternalServiceError
from deckforge.db.models.user import User
from deckforge.services.dto import UserDTO

pytestmark = pytest.mark.asyncio


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_without_token(auth_client: AsyncClient):
    response = await auth_client.get(url="/api/decks/")

    assert response.status_code == 401


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_with_invalid_token(
    auth_client: AsyncClient,
):
    response = await auth_client.get(
        url="/api/decks/", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_with_token_without_sub(
    auth_client: AsyncClient, jwt_adapter
):
    token = jwt_adapter.create_access_token(data={})
    response = await auth_client.get(
        url="/api/decks/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_with_token_without_user_in_db(
    auth_client: AsyncClient, jwt_adapter
):
    token = jwt_adapter.create_access_token(data={"sub": str(uuid.uuid4())})
    response = await auth_client.get(
        url="/api/decks/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_with_valid_user_and_token(
    auth_client: AsyncClient, test_user: UserDTO, jwt_adapter
):
    token = jwt_adapter.create_access_token(data={"sub": str(test_user.id)})
    response = await auth_client.get(
        url="/api/decks/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []


@allure.feature("Authentication")
@allure.story("Token authentication")
async def test_protected_endpoint_with_expired_token(
    auth_client: AsyncClient, test_user: UserDTO, jwt_adapter
):
    token = jwt_adapter.create_access_token(
        data={"sub": str(test_user.id)}, expire_delta=timedelta(days=-10)
    )
    response = await auth_client.get(
        url="/api/decks/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


@allure.feature("Authentication")
@allure.story("Google OAuth callback")
async def test_google_callback_creates_user(
    auth_client: AsyncClient, db_session: AsyncSession, fake_oauth, jwt_adapter
):
    response = await auth_client.get(
        url="/auth/google/callback", follow_redirects=False
    )

    assert response.status_code in {302, 307}

    location = response.headers["location"]
    assert location.startswith("http://frontend.test/app?token=")

    parsed_url = urlparse(location)
    query = parse_qs(parsed_url.query)
    token = query["token"][0]

    payload = jwt_adapter.decode_access_token(token)
    user_id = payload["sub"]

    res = await db_session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one()

    assert user.email == "user@example.com"
    assert user.google_id == "google-user-id"
    assert user.name == "Test User"


@allure.feature("Authentication")
@allure.story("Google OAuth callback")
async def test_google_callback_reuses_an_existing_user(
    auth_client: AsyncClient, db_session: AsyncSession, fake_oauth
):
    user = User(email="user@example.com", name="Test User", google_id="google-user-id")
    db_session.add(user)
    await db_session.commit()

    response = await auth_client.get(
        url="/auth/google/callback/", follow_redirects=False
    )

    assert response.status_code in {302, 307}

    res = await db_session.execute(select(User).where(User.google_id == user.google_id))
    users = res.scalars().all()

    assert len(users) == 1
    assert users[0].id == user.id


@allure.feature("Authentication")
@allure.story("Google OAuth callback")
async def test_oauth_error_turns_into_400(auth_client: AsyncClient, fake_oauth):
    fake_oauth.authorize_error = OAuthError("oauth failed")
    response = await auth_client.get(url="/auth/google/callback")

    assert response.status_code == 400
    assert "oauth failed" in response.json()["detail"]


@allure.feature("Authentication")
@allure.story("Google OAuth callback")
async def test_external_error_turns_into_502(auth_client: AsyncClient, fake_oauth):
    fake_oauth.authorize_error = ExternalServiceError()
    response = await auth_client.get(url="/auth/google/callback")

    assert response.status_code == 502
    assert (
        "Google OAuth service is temporarily unavailable" in response.json()["detail"]
    )
