import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from deckforge.adapters.errors import ExternalServiceError
from deckforge.config import SecurityConfig


class GoogleOAuthAdapter:
    def __init__(self, config: SecurityConfig):
        self._oauth = OAuth()
        self._oauth.register(
            "google",
            client_id=config.google_client_id,
            client_secret=config.google_client_secret,
            scope=["openid", "email", "profile"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        )

    async def get_google_redirect(self, request: Request, redirect_uri: str):
        return await self._oauth.google.authorize_redirect(
            request, redirect_uri=redirect_uri
        )

    async def authorize_access_token(self, request: Request):
        for attempt in range(2):
            try:
                return await self._oauth.google.authorize_access_token(request)
            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise ExternalServiceError(
                    "Failed to reach Google OAuth endpoints"
                ) from e


class JWTAdapter:
    def __init__(self, config: SecurityConfig):
        self._config = config

    def create_access_token(self, data: dict, expire_delta: timedelta | None = None):
        to_encode = data.copy()
        if expire_delta:
            expire = datetime.now(timezone.utc) + expire_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=30)
        to_encode["exp"] = expire
        to_encode["auth_method"] = "google"
        encoded_jwt = jwt.encode(
            to_encode,
            self._config.jwt_secret,
            algorithm="HS256",
        )
        # PyJWT 1.x returns bytes; normalize to str for URL/query usage.
        if isinstance(encoded_jwt, bytes):
            return encoded_jwt.decode("utf-8")
        return encoded_jwt

    def decode_access_token(self, token: str):
        return jwt.decode(
            token,
            self._config.jwt_secret,
            algorithms=["HS256"],
        )
