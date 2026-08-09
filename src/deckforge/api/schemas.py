import uuid

from pydantic import BaseModel


class DeckTaskCreateRequest(BaseModel):
    words: list[str]
    options: dict


class DeckTaskCreateResponse(BaseModel):
    task_id: uuid.UUID


class DeckTaskItemStatusResponse(BaseModel):
    raw_word: str
    status: str
    stage: str | None


class DeckTaskStatusResponse(BaseModel):
    status: str
    items: list[DeckTaskItemStatusResponse]


class DeckTaskResponce(BaseModel):
    id: uuid.UUID
    status: str
    total_items: int


class DeckCardResponse(BaseModel):
    id: uuid.UUID
    word: str
    sentence: str
    translation: str


class DeckCardsResponse(BaseModel):
    task_id: uuid.UUID
    suggested_deck_name: str
    cards: list[DeckCardResponse]
