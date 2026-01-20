import uuid

from fastapi import APIRouter

from deckforge.api.schemas import DeckTaskCreateRequest

router = APIRouter(prefix="/decks")


@router.post("/")
async def create_task(task: DeckTaskCreateRequest):
    pass


@router.get("/{task_id}/status")
async def get_status(task_id: uuid.UUID):
    pass


@router.get("/{task_id}/result")
async def get_deck(task_id: uuid.UUID):
    pass
