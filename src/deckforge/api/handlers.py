import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from deckforge.api.schemas import DeckTaskCreateRequest
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckTaskCreateDTO

router = APIRouter(prefix="/decks", route_class=DishkaRoute)


@router.post("/")
async def create_task(
    task: DeckTaskCreateRequest, service: FromDishka[DeckTaskService]
):
    task_dto = DeckTaskCreateDTO(**task.model_dump())
    await service.create_task(task_dto)

    return {"status": "unknown"}


@router.get("/{task_id}/status")
async def get_status(task_id: uuid.UUID):
    pass


@router.get("/{task_id}/result")
async def get_deck(task_id: uuid.UUID):
    pass
