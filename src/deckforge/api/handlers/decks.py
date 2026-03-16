import uuid
from typing import Annotated, List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from deckforge.api.handlers.auth import get_current_user
from deckforge.api.schemas import DeckTaskCreateRequest, DeckTaskResponce
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckTaskCreateDTO, UserDTO
from deckforge.services.errors import NotFoundError

router = APIRouter(
    prefix="/decks",
    route_class=DishkaRoute,
    tags=[
        "Decks",
    ],
)


@router.post("/")
async def create_task(
    task: DeckTaskCreateRequest,
    service: FromDishka[DeckTaskService],
    current_user: Annotated[UserDTO, Depends(get_current_user)],
):
    task_dto = DeckTaskCreateDTO(**task.model_dump())
    return await service.create_task(task_dto, current_user.id)


@router.get("/")
async def get_tasks(
    service: FromDishka[DeckTaskService],
    current_user: Annotated[UserDTO, Depends(get_current_user)],
) -> List[DeckTaskResponce]:
    try:
        tasks = await service.get_tasks(current_user.id)
        response_tasks = [
            DeckTaskResponce(
                id=task.id, status=task.status, total_items=task.total_items
            )
            for task in tasks
        ]
        return response_tasks
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{task_id}/status")
async def get_status(
    task_id: uuid.UUID,
    service: FromDishka[DeckTaskService],
    current_user: Annotated[UserDTO, Depends(get_current_user)],
):
    try:
        task = await service.get_task(task_id)
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        return task.status
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{item_id}/result")
async def get_deck(item_id: uuid.UUID):
    return FileResponse(
        path=f"media/{item_id}.apkg", media_type="application/octet-stream"
    )
