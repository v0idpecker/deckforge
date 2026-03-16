from fastapi import APIRouter

from deckforge.api.handlers.auth import router as auth_router
from deckforge.api.handlers.decks import router as decks_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(decks_router)
