import uuid
from dataclasses import dataclass

from deckforge.db.models.outbox import EventStatus, OutboxEvent


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
