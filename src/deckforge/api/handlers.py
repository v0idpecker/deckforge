import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from fastapi.responses import FileResponse

from deckforge.api.schemas import DeckTaskCreateRequest
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckTaskCreateDTO

router = APIRouter(prefix="/decks", route_class=DishkaRoute)


@router.post("/")
async def create_task(
    task: DeckTaskCreateRequest, service: FromDishka[DeckTaskService]
):
    task_dto = DeckTaskCreateDTO(**task.model_dump())
    return await service.create_task(task_dto)


@router.get("/{task_id}/status")
async def get_status(task_id: uuid.UUID, service: FromDishka[DeckTaskService]):
    return service.get_task_status(task_id)


@router.get("/{item_id}/result")
async def get_deck(item_id: uuid.UUID):
    return FileResponse(
        path=f"media/{item_id}.apkg", media_type="application/octet-stream"
    )
