import uuid
from dataclasses import dataclass

from deckforge.db.models.decks import DeckCard


@dataclass
class DeckCardDTO:
    id: uuid.UUID
    task_id: uuid.UUID
    item_id: uuid.UUID
    word: str
    target_word_form: str | None
    sentence: str
    translation: str
    position: int

    @classmethod
    def from_entity(cls, entity: DeckCard):
        return cls(
            id=entity.id,
            task_id=entity.task_id,
            item_id=entity.item_id,
            word=entity.word,
            target_word_form=entity.target_word_form,
            sentence=entity.sentence,
            translation=entity.translation,
            position=entity.position,
        )


@dataclass
class DeckCardCreateDTO:
    task_id: uuid.UUID
    item_id: uuid.UUID
    word: str
    sentence: str
    translation: str
    position: int
    target_word_form: str | None = None
