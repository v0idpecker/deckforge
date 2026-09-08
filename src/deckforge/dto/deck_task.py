import datetime
import uuid
from dataclasses import dataclass

from deckforge.db.models.decks import DeckTask

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
    user_id: uuid.UUID | None
    attempt_count: int
    next_retry_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def from_entity(cls, entity: DeckTask) -> "DeckTaskDTO":
        return cls(
            id=entity.id,
            status=entity.status,
            current_stage=entity.current_stage,
            total_items=entity.total_items,
            completed_items=entity.completed_items,
            failed_items=entity.failed_items,
            options=entity.options,
            error=entity.error,
            user_id=entity.user_id,
            attempt_count=entity.attempt_count,
            next_retry_at=entity.next_retry_at,
            updated_at=entity.updated_at,
        )

@dataclass
class DeckTaskCreateDTO:
    words: list[str]
    options: dict
