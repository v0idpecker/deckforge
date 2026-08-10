from typing import List
from uuid import UUID

from genanki import Deck, Model, Note, Package

from deckforge.dto.deck_card import DeckCardDTO

DECKFORGE_MODEL = Model(
    model_id=1356227795,
    name="DeckForge Basic",
    fields=[{"name": "Sentence"}, {"name": "Translation"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Sentence}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Translation}}',
        }
    ],
)


class AnkiAdapter:
    def export_deck(
        self, task_id: UUID, deck_name: str, cards: List[DeckCardDTO]
    ) -> str:
        deck = Deck(deck_id=task_id.int % (1 << 31), name=deck_name)
        for card in cards:
            note = Note(model=DECKFORGE_MODEL, fields=[card.sentence, card.translation])
            deck.add_note(note)
        path = f"media/{task_id}.apkg"
        Package(deck).write_to_file(path)

        return path
