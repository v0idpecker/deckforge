import uuid
from dataclasses import dataclass


@dataclass
class DeckTaskDTO:
    id: uuid.UUID
    status: str
    current_stage: str
    total_items: int
    completed_items: int
    failed_items: int
    options: dict
    error: str


@dataclass
class DeckItemDTO:
    id: uuid.UUID
    task_id: uuid.UUID
    raw_word: str
    normalized_word: str
    status: str
    stage: str
    sentence: str
    translation: str
    error: str


@dataclass
class DeckTaskCreateDTO:
    words: list[str]
    options: dict


@dataclass
class DeckItemCreateDTO:
    task_id: uuid.UUID
    raw_word: str
