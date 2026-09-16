import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DeckTaskOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalization: bool = False
    limit: int = Field(default=1, ge=1, le=5)
    sentence_lang: Literal["english", "german", "spanish", "french", "italian"] = "english"
    translation_lang: Literal["russian", "english", "german", "spanish", "french"] = "russian"
    difficulty: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = "B1"
    card_format: Literal["basic", "cloze"] = "basic"
    add_reverse: bool = False


class DeckTaskCreateRequest(BaseModel):
    words: list[str]
    options: DeckTaskOptions


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
    target_word_form: str | None = None


class DeckCardsResponse(BaseModel):
    task_id: uuid.UUID
    suggested_deck_name: str
    card_format: Literal["basic", "cloze"] = "basic"
    cards: list[DeckCardResponse]
