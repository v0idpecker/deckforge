from datetime import datetime, timedelta, timezone

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Request

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
        return await self._oauth.google.authorize_access_token(request)


class JWTAdapter:
    def __init__(self, config: SecurityConfig):
        self._config = config

    def create_access_token(self, data: dict, expire_delta: timedelta | None = None):
        to_encode = data.copy()
        if expire_delta:
            expire = datetime.now(timezone.utc) + expire_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode["exp"] = expire
        to_encode["auth_method"] = "google"
        encoded_jwt = jwt.encode(
            to_encode,
            self._config.jwt_secret,
            algorithm="HS256",
        )
        return encoded_jwt

    def decode_access_token(self, token: str):
        return jwt.decode(
            token,
            self._config.jwt_secret,
            algorithm="HS256",
        )
