import random

from genanki import Deck, Model, Note, Package


class AnkiAdapter:
    def __init__(self):
        self.basic_model = Model(
            model_id=random.randrange(1 << 30, 1 << 31),
            name="Basic",
            fields=[{"name": "Sentence"}, {"name": "Translation"}],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Sentence}}",
                    "afmt": '{{FrontSide}}<hr id="answer">{{Translation}}',
                }
            ],
        )
        self.deck = Deck(
            deck_id=random.randrange(1 << 30, 1 << 31),
            name=str(random.randrange(1 << 30, 1 << 31)),
        )

    def add_card(self, sentence: str, translation: str):
        note = Note(model=self.basic_model, fields=[sentence, translation])
        self.deck.add_note(note)

    def export_deck(self, card_id: str):
        Package(self.deck).write_to_file(f"media/{card_id}.apkg")
