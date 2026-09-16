from fastapi import APIRouter

from ankislop.api.handlers.auth import router as auth_router
from ankislop.api.handlers.decks import router as decks_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(decks_router)
