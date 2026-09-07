from uuid import UUID

import allure
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.adapters.errors import ExternalServiceError
from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.services.errors import ServiceError

pytestmark = pytest.mark.asyncio


@allure.feature("Pipeline")
@allure.story("Item error handling")
async def test_service_error_in_item_marks_item_error_and_task_partially_done(
    client: AsyncClient,
    pipeline,
    fake_context_generator,
    db_session: AsyncSession,
):
    response = await client.post(
        url="/api/decks/",
        json={"words": ["cat", "dog"], "options": {"normalization": True, "limit": 1}},
    )
    task_id = UUID(response.json()["task_id"])

    fake_context_generator.words_to_fail_with["cat"] = ServiceError("context failed")

    await pipeline.run(task_id)

    # expire_all() у AsyncSession — синхронный метод, await не нужен
    db_session.expire_all()
    res = await db_session.execute(select(DeckItem).where(DeckItem.task_id == task_id))
    items = res.scalars().all()
    items_by_word = {item.raw_word: item for item in items}

    assert items_by_word["cat"].status == "ERROR"
    assert items_by_word["cat"].error == "context failed"
    assert items_by_word["dog"].status == "DONE"

    res = await db_session.execute(select(DeckTask).where(DeckTask.id == task_id))
    task = res.scalar_one()

    assert task.status == "PARTIALLY_DONE"


@allure.feature("Pipeline")
@allure.story("Item error handling")
async def test_arbitrary_exception_in_item_marks_item_error_and_task_partially_done(
    client: AsyncClient,
    pipeline,
    fake_context_generator,
    db_session: AsyncSession,
):
    response = await client.post(
        url="/api/decks/",
        json={"words": ["cat", "dog"], "options": {"normalization": True, "limit": 1}},
    )
    task_id = UUID(response.json()["task_id"])

    fake_context_generator.words_to_fail_with["dog"] = RuntimeError("kaboom")

    # произвольное исключение не должно ронять pipeline
    await pipeline.run(task_id)

    # expire_all() у AsyncSession — синхронный метод, await не нужен
    db_session.expire_all()
    res = await db_session.execute(select(DeckItem).where(DeckItem.task_id == task_id))
    items = res.scalars().all()
    items_by_word = {item.raw_word: item for item in items}

    assert items_by_word["dog"].status == "ERROR"
    assert items_by_word["dog"].error == "kaboom"
    assert items_by_word["cat"].status == "DONE"

    res = await db_session.execute(select(DeckTask).where(DeckTask.id == task_id))
    task = res.scalar_one()

    assert task.status == "PARTIALLY_DONE"


@allure.feature("Pipeline")
@allure.story("Item error handling")
async def test_invalid_llm_response_twice_fills_item_error(
    client: AsyncClient,
    db_session: AsyncSession,
    make_llm_pipeline,
    make_llm_response,
    fake_anki,
):
    response = await client.post(
        url="/api/decks/",
        json={"words": ["cat"], "options": {"normalization": True, "limit": 1}},
    )
    task_id = UUID(response.json()["task_id"])

    responses = [
        make_llm_response(parsed=None, content="{invalid json"),
        make_llm_response(parsed=None, content="{invalid json"),
    ]
    llm_pipeline = make_llm_pipeline(responses)

    with pytest.raises(ExternalServiceError) as exc_info:
        await llm_pipeline.run(task_id)

    assert str(exc_info.value)

    # expire_all() у AsyncSession — синхронный метод, await не нужен
    db_session.expire_all()
    res = await db_session.execute(select(DeckItem).where(DeckItem.task_id == task_id))
    item = res.scalar_one()

    assert item.status == "ERROR"
    assert item.error
    assert fake_anki.export_calls == []
