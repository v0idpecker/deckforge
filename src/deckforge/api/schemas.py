import uuid

from pydantic import BaseModel


class DeckTaskCreateRequest(BaseModel):
    words: list[str]
    options: dict


class DeckTaskResponce(BaseModel):
    id: uuid.UUID
    status: str
    total_items: int
