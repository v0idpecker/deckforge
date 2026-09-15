import uuid

import allure
import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select

from deckforge.db.models.decks import DeckCard, DeckItem, DeckTask
from deckforge.dto.deck_card import DeckCardCreateDTO
from deckforge.dto.user import UserDTO
from deckforge.services.decks.deckcard import DeckCardService

pytestmark = pytest.mark.asyncio


async def make_task_with_item(
    db_session: AsyncSession, test_user: UserDTO
) -> tuple[uuid.UUID, uuid.UUID]:
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={"limit": 2},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()
    return task.id, item.id


async def fetch_cards(db_session: AsyncSession, item_id: uuid.UUID):
    result = await db_session.execute(
        select(DeckCard)
        .where(DeckCard.item_id == item_id)
        .order_by(DeckCard.position)
    )
    return result.scalars().all()


@allure.feature("Deck cards")
@allure.story("target_word_form persistence")
async def test_replace_for_item_persists_target_word_form(
    deckcard_service: DeckCardService, db_session: AsyncSession, test_user: UserDTO
):
    task_id, item_id = await make_task_with_item(db_session, test_user)
    cards = [
        DeckCardCreateDTO(
            task_id=task_id,
            item_id=item_id,
            word="cat",
            sentence="The cat sleeps.",
            translation="Кот спит.",
            position=0,
            target_word_form="cat",
        ),
        DeckCardCreateDTO(
            task_id=task_id,
            item_id=item_id,
            word="cat",
            sentence="A cat was sleeping.",
            translation="Кот спал.",
            position=1,
            target_word_form=None,
        ),
    ]

    await deckcard_service.replace_for_item(item_id, cards)

    db_session.expire_all()
    stored = await fetch_cards(db_session, item_id)

    assert len(stored) == 2
    assert stored[0].target_word_form == "cat"
    assert stored[1].target_word_form is None


@allure.feature("Deck cards")
@allure.story("target_word_form persistence")
async def test_replace_for_item_defaults_to_null_target_word_form(
    deckcard_service: DeckCardService, db_session: AsyncSession, test_user: UserDTO
):
    task_id, item_id = await make_task_with_item(db_session, test_user)
    cards = [
        DeckCardCreateDTO(
            task_id=task_id,
            item_id=item_id,
            word="cat",
            sentence="The cat sleeps.",
            translation="Кот спит.",
            position=0,
        )
    ]

    await deckcard_service.replace_for_item(item_id, cards)

    db_session.expire_all()
    stored = await fetch_cards(db_session, item_id)

    assert len(stored) == 1
    assert stored[0].target_word_form is None


@allure.feature("Deck cards")
@allure.story("target_word_form persistence")
async def test_retry_replace_updates_target_word_form(
    deckcard_service: DeckCardService, db_session: AsyncSession, test_user: UserDTO
):
    task_id, item_id = await make_task_with_item(db_session, test_user)
    first = [
        DeckCardCreateDTO(
            task_id=task_id,
            item_id=item_id,
            word="cat",
            sentence="The cat sleeps.",
            translation="Кот спит.",
            position=0,
        )
    ]

    await deckcard_service.replace_for_item(item_id, first)

    second = [
        DeckCardCreateDTO(
            task_id=task_id,
            item_id=item_id,
            word="cat",
            sentence="The cat sleeps.",
            translation="Кот спит.",
            position=0,
            target_word_form="cat",
        )
    ]

    await deckcard_service.replace_for_item(item_id, second)

    db_session.expire_all()
    stored = await fetch_cards(db_session, item_id)

    assert len(stored) == 1
    assert stored[0].target_word_form == "cat"
