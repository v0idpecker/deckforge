import datetime
import uuid
from dataclasses import dataclass

from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.db.models.outbox import EventStatus, OutboxEvent
from deckforge.db.models.user import User


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
        )


@dataclass
class DeckItemDTO:
    id: uuid.UUID
    task_id: uuid.UUID
    raw_word: str
    normalized_word: str | None
    status: str
    stage: str
    sentence: str
    translation: str
    error: str

    @classmethod
    def from_entity(cls, entity: DeckItem) -> "DeckItemDTO":
        return cls(
            id=entity.id,
            task_id=entity.task_id,
            raw_word=entity.raw_word,
            normalized_word=entity.normalized_word,
            status=entity.status,
            stage=entity.stage,
            sentence=entity.sentence,
            translation=entity.translation,
            error=entity.error,
        )


@dataclass
class DeckTaskCreateDTO:
    words: list[str]
    options: dict


@dataclass
class DeckItemCreateDTO:
    task_id: uuid.UUID
    raw_word: str


@dataclass
class UserDTO:
    id: uuid.UUID
    name: str | None
    email: str
    google_id: str | None

    @classmethod
    def from_entity(cls, entity: User) -> "UserDTO":
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            google_id=entity.google_id,
        )


@dataclass
class UserCreateDTO:
    name: str | None
    email: str | None
    google_id: str | None


@dataclass
class OutboxEventDTO:
    id: uuid.UUID
    payload: dict
    event_type: str
    status: EventStatus

    @classmethod
    def from_entity(cls, entity: OutboxEvent) -> "OutboxEventDTO":
        return cls(
            id=entity.id,
            payload=entity.payload,
            event_type=entity.event_type,
            status=entity.status,
        )


@dataclass
class OutboxEventCreateDTO:
    payload: dict
    event_type: str
