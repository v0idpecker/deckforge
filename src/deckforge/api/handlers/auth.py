from datetime import timedelta
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka, inject
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from deckforge.adapters.security import GoogleOAuthAdapter, JWTAdapter
from deckforge.services.dto import UserCreateDTO, UserDTO
from deckforge.services.user import UserService

router = APIRouter(
    prefix="/auth",
    route_class=DishkaRoute,
    tags=[
        "Auth",
    ],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/google")
async def auth_google(request: Request, oauth: FromDishka[GoogleOAuthAdapter]):
    return await oauth.get_google_redirect(
        request, redirect_uri="http://127.0.0.1:8000/auth/google/callback"
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    service: FromDishka[UserService],
    oauth: FromDishka[GoogleOAuthAdapter],
    jwt: FromDishka[JWTAdapter],
):
    token = await oauth.authorize_access_token(request)
    user_info = token.get("userinfo") or {}

    user = await service.get_or_create(
        UserCreateDTO(
            google_id=user_info.get("sub"),
            email=user_info.get("email"),
            name=user_info.get("name"),
        )
    )

    access_token = jwt.create_access_token(
        {"sub": str(user.id)}, expire_delta=timedelta(days=30)
    )
    return RedirectResponse(url=f"http://localhost:5173/app?token={access_token}")


@inject
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt: FromDishka[JWTAdapter],
    service: FromDishka[UserService],
) -> UserDTO:
    try:
        payload = jwt.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
