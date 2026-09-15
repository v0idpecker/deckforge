import html
import re
import uuid
from typing import List

from genanki import Deck, Model, Note, Package

from deckforge.dto.deck_card import DeckCardDTO

BASIC_MODEL_ID = 1932635215
CLOZE_MODEL_ID = 2063421052

MODEL_CSS = """.card {
  font-family: Arial, sans-serif;
  font-size: 22px;
  text-align: center;
  color: #1a1c1e;
  background-color: #f3f5f7;
  padding: 24px;
}
.sentence {
  font-size: 26px;
  line-height: 1.4;
  margin-bottom: 16px;
}
.target-word {
  font-weight: 700;
  color: #0d9488;
}
.translation {
  color: #555;
}
.nightMode .card {
  color: #e4e6e8;
  background-color: #1a1c1e;
}
.nightMode .translation {
  color: #a8abae;
}
.nightMode .target-word {
  color: #2dd4bf;
}"""

BASIC_MODEL_NAME = "DeckForge Context"
CLOZE_MODEL_NAME = "DeckForge Cloze"


def build_basic_model(add_reverse: bool) -> Model:
    templates = [
        {
            "name": "Card 1",
            "qfmt": '<div class="sentence">{{Sentence}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer"><div class="translation">{{Translation}}</div>',
        }
    ]
    if add_reverse:
        templates.append(
            {
                "name": "Card 2 (reverse)",
                "qfmt": '<div class="translation">{{Translation}}</div>',
                "afmt": '{{FrontSide}}<hr id="answer"><div class="sentence">{{Sentence}}</div>',
            }
        )
    return Model(
        model_id=BASIC_MODEL_ID,
        name=BASIC_MODEL_NAME,
        fields=[{"name": "Sentence"}, {"name": "Translation"}],
        templates=templates,
        css=MODEL_CSS,
    )


def build_cloze_model() -> Model:
    return Model(
        model_id=CLOZE_MODEL_ID,
        name=CLOZE_MODEL_NAME,
        model_type=Model.CLOZE,
        fields=[{"name": "Sentence"}, {"name": "Translation"}],
        templates=[
            {
                "name": "Cloze",
                "qfmt": '<div class="sentence">{{cloze:Sentence}}</div>',
                "afmt": '{{cloze:Sentence}}<hr id="answer"><div class="translation">{{Translation}}</div>',
            }
        ],
        css=MODEL_CSS,
    )


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


def highlight_sentence(sentence: str, form: str | None) -> str:
    escaped = escape_html(sentence)
    if not form:
        return escaped
    escaped_form = re.escape(escape_html(form.strip()))
    if not escaped_form:
        return escaped
    pattern = re.compile(escaped_form, re.IGNORECASE)
    return pattern.sub(
        lambda m: f'<span class="target-word">{m.group(0)}</span>', escaped, count=1
    )


def cloze_sentence(sentence: str, form: str | None) -> str:
    if form:
        normalized = form.strip()
        if normalized:
            escaped = escape_html(sentence)
            escaped_form = re.escape(escape_html(normalized))
            pattern = re.compile(escaped_form, re.IGNORECASE)
            if pattern.search(escaped):
                return pattern.sub(
                    lambda m: f"{{{{c1::{m.group(0)}}}}}", escaped, count=1
                )
    return escape_html(sentence)


class AnkiAdapter:
    def export_deck(
        self,
        task_id: uuid.UUID,
        deck_name: str,
        cards: List[DeckCardDTO],
        options: dict | None = None,
    ) -> str:
        options = options or {}
        card_format = options.get("card_format", "basic")
        add_reverse = bool(options.get("add_reverse", False))

        if card_format == "cloze":
            model = build_cloze_model()
        else:
            model = build_basic_model(add_reverse)

        deck = Deck(deck_id=task_id.int % (1 << 31), name=deck_name)
        for card in cards:
            if card_format == "cloze":
                sentence = cloze_sentence(card.sentence, card.target_word_form)
            else:
                sentence = highlight_sentence(card.sentence, card.target_word_form)
            note = Note(
                model=model,
                fields=[sentence, escape_html(card.translation)],
            )
            deck.add_note(note)
        path = f"media/{task_id}.apkg"
        Package(deck).write_to_file(path)

        return path
