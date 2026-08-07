import uuid
from dataclasses import dataclass

from deckforge.db.models.decks import DeckItem


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
class DeckItemCreateDTO:
    task_id: uuid.UUID
    raw_word: str
