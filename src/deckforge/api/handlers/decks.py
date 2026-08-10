import uuid
from typing import Annotated, List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from deckforge.api.handlers.auth import get_current_user
from deckforge.api.schemas import (
    DeckCardResponse,
    DeckCardsResponse,
    DeckTaskCreateRequest,
    DeckTaskCreateResponse,
    DeckTaskItemStatusResponse,
    DeckTaskResponce,
    DeckTaskStatusResponse,
)
from deckforge.dto.deck_task import DeckTaskCreateDTO
from deckforge.dto.user import UserDTO
from deckforge.services.decks.deckcard import DeckCardService
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.errors import NotFoundError

router = APIRouter(
    prefix="/api/decks",
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
) -> DeckTaskCreateResponse:
    task_dto = DeckTaskCreateDTO(**task.model_dump())
    task_id = await service.create_task(task_dto, current_user.id)
    return DeckTaskCreateResponse(task_id=task_id)


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
    except NotFoundError:
        return []


@router.get("/{task_id}/status")
async def get_status(
    task_id: uuid.UUID,
    service: FromDishka[DeckTaskService],
    current_user: Annotated[UserDTO, Depends(get_current_user)],
) -> DeckTaskStatusResponse:
    try:
        task = await service.get_task(task_id)
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        items = await service.get_task_items(task_id)
        return DeckTaskStatusResponse(
            status=task.status,
            items=[
                DeckTaskItemStatusResponse(
                    raw_word=item.raw_word,
                    status=item.status,
                    stage=None if item.stage == "NONE" else item.stage,
                )
                for item in items
            ],
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{task_id}/result")
async def get_deck(
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
        deck_path = await service.get_result_path(task_id)
        return FileResponse(path=deck_path, media_type="application/octet-stream")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{task_id}/cards")
async def get_cards(
    task_id: uuid.UUID,
    card_service: FromDishka[DeckCardService],
    task_service: FromDishka[DeckTaskService],
    current_user: Annotated[UserDTO, Depends(get_current_user)],
):
    try:
        task = await task_service.get_task(task_id)
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        cards = await card_service.list_by_task(task_id)
        cards_for_response = []
        for card in cards:
            cards_for_response.append(
                DeckCardResponse(
                    id=card.id,
                    word=card.word,
                    sentence=card.sentence,
                    translation=card.translation,
                )
            )

        deck_name = task_service.derive_deck_name(task.options)

        return DeckCardsResponse(
            task_id=task_id,
            suggested_deck_name=deck_name,
            cards=cards_for_response,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
