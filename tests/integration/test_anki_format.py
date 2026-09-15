import uuid

import allure
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.adapters.anki import (
    BASIC_MODEL_ID,
    CLOZE_MODEL_ID,
    AnkiAdapter,
    build_basic_model,
    build_cloze_model,
    cloze_sentence,
    escape_html,
    highlight_sentence,
)
from deckforge.db.models.decks import DeckCard, DeckItem, DeckTask
from deckforge.dto.deck_card import DeckCardDTO
from deckforge.dto.user import UserDTO

pytestmark = pytest.mark.asyncio


def make_card(
    sentence: str,
    translation: str = "Кот спит.",
    form: str | None = "cat",
    position: int = 0,
) -> DeckCardDTO:
    return DeckCardDTO(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        item_id=uuid.uuid4(),
        word="cat",
        target_word_form=form,
        sentence=sentence,
        translation=translation,
        position=position,
    )


@allure.feature("Anki adapter")
@allure.story("Models")
def test_basic_model_has_single_template_and_new_id():
    model = build_basic_model(add_reverse=False)

    assert model.model_id == BASIC_MODEL_ID
    assert BASIC_MODEL_ID != 1356227795
    assert len(model.templates) == 1


@allure.feature("Anki adapter")
@allure.story("Models")
def test_basic_model_with_reverse_has_two_templates():
    model = build_basic_model(add_reverse=True)

    assert len(model.templates) == 2
    assert "reverse" in model.templates[1]["name"]


@allure.feature("Anki adapter")
@allure.story("Models")
def test_cloze_model_is_cloze_type_with_new_id():
    model = build_cloze_model()

    assert model.model_id == CLOZE_MODEL_ID
    assert model.model_type == model.CLOZE


@allure.feature("Anki adapter")
@allure.story("Highlighting")
def test_highlight_wraps_first_occurrence_case_insensitive():
    result = highlight_sentence("The CAT sleeps all day.", "cat")

    assert result == (
        'The <span class="target-word">CAT</span> sleeps all day.'
    )


@allure.feature("Anki adapter")
@allure.story("Highlighting")
def test_highlight_without_form_returns_escaped_sentence():
    result = highlight_sentence("The cat & the <dog> sleep.", None)

    assert result == "The cat &amp; the &lt;dog&gt; sleep."


@allure.feature("Anki adapter")
@allure.story("Highlighting")
def test_highlight_with_absent_form_returns_escaped_sentence():
    result = highlight_sentence("The dog sleeps.", "cat")

    assert "<span" not in result
    assert "&" not in result or "cat" not in result


@allure.feature("Anki adapter")
@allure.story("Highlighting")
def test_highlight_escapes_html_specials():
    result = highlight_sentence("Cat & <dog> play.", "cat")

    assert "&amp;" in result
    assert "&lt;dog&gt;" in result
    assert '<span class="target-word">Cat</span>' in result


@allure.feature("Anki adapter")
@allure.story("Cloze")
def test_cloze_wraps_word_form():
    result = cloze_sentence("The cat sleeps.", "cat")

    assert result == "The {{c1::cat}} sleeps."


@allure.feature("Anki adapter")
@allure.story("Cloze")
def test_cloze_falls_back_to_plain_sentence_without_form():
    result = cloze_sentence("The dog sleeps.", "cat")

    assert result == "The dog sleeps."
    assert "{{c1::" not in result


@allure.feature("Anki adapter")
@allure.story("Cloze")
def test_cloze_escapes_html_specials():
    result = cloze_sentence("Cat & <dog> play.", "cat")

    assert result == "{{c1::Cat}} &amp; &lt;dog&gt; play."


@allure.feature("Anki adapter")
@allure.story("escape html")
def test_escape_html_keeps_quotes():
    assert escape_html('a "b" c') == 'a "b" c'
    assert escape_html("a & b < c > d") == "a &amp; b &lt; c &gt; d"


@allure.feature("Anki adapter")
@allure.story("Export")
async def test_export_deck_basic_creates_file_with_highlighted_cards(
    tmp_path, test_user: UserDTO, db_session: AsyncSession, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "media").mkdir()
    task_id = uuid.uuid4()
    cards = [make_card("The cat sleeps.")]

    adapter = AnkiAdapter()
    path = adapter.export_deck(
        task_id, "DeckForge::english→russian", cards, {"card_format": "basic"}
    )

    try:
        assert (tmp_path / "media" / f"{task_id}.apkg").is_file()
        assert path == f"media/{task_id}.apkg"
    finally:
        (tmp_path / "media" / f"{task_id}.apkg").unlink(missing_ok=True)


@allure.feature("Anki adapter")
@allure.story("Export")
async def test_export_deck_cloze_creates_file(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "media").mkdir()
    task_id = uuid.uuid4()
    cards = [make_card("The cat sleeps.")]

    adapter = AnkiAdapter()
    adapter.export_deck(
        task_id, "DeckForge::english→russian", cards, {"card_format": "cloze"}
    )

    try:
        assert (tmp_path / "media" / f"{task_id}.apkg").is_file()
    finally:
        (tmp_path / "media" / f"{task_id}.apkg").unlink(missing_ok=True)


@allure.feature("Anki adapter")
@allure.story("Export")
async def test_export_deck_without_options_defaults_to_basic(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "media").mkdir()
    task_id = uuid.uuid4()
    cards = [make_card("The cat sleeps.", form=None)]

    adapter = AnkiAdapter()
    adapter.export_deck(task_id, "deck", cards, None)

    try:
        assert (tmp_path / "media" / f"{task_id}.apkg").is_file()
    finally:
        (tmp_path / "media" / f"{task_id}.apkg").unlink(missing_ok=True)


@allure.feature("Anki adapter")
@allure.story("Export")
async def test_pipeline_passes_options_and_form_to_export(
    pipeline,
    fake_anki,
    db_session: AsyncSession,
    test_user: UserDTO,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
            "card_format": "cloze",
            "add_reverse": True,
        },
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()
    db_session.add(DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id))
    await db_session.commit()
    task_id = task.id

    await pipeline.run(task_id)

    assert len(fake_anki.export_calls) == 1
    _, _, exported_cards, exported_options = fake_anki.export_calls[0]
    assert exported_options["card_format"] == "cloze"
    assert exported_options["add_reverse"] is True
    assert exported_cards[0].target_word_form == "cat"


@allure.feature("Anki adapter")
@allure.story("Export")
async def test_pipeline_old_options_export_as_basic(
    pipeline,
    fake_anki,
    db_session: AsyncSession,
    test_user: UserDTO,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={"limit": 1},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()
    db_session.add(DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id))
    await db_session.commit()
    task_id = task.id

    await pipeline.run(task_id)

    assert len(fake_anki.export_calls) == 1
    _, _, _, exported_options = fake_anki.export_calls[0]
    assert "card_format" not in exported_options
