import asyncio
import uuid

import allure
import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import select

from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.services.dto import UserDTO
from deckforge.services.errors import NotFoundError

pytestmark = pytest.mark.asyncio


@allure.feature("Deck pipeline")
@allure.story("Task lifecycle")
async def test_pipeline_turns_pending_task_into_done(
    pipeline: DeckPipeline, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={},
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_task.status == "DONE"
    assert new_item.status == "DONE"
    assert new_item.stage == "DONE"
    assert not new_item.normalized_word
    assert not new_item.sentence
    assert not new_item.translation


@allure.feature("Deck pipeline")
@allure.story("Task lifecycle")
async def test_task_with_done_status_is_not_processing_again(
    pipeline: DeckPipeline, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="DONE",
        current_stage="NONE",
        total_items=1,
        options={},
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_task.status == "DONE"
    assert new_item.status == "PENDING"
    assert new_item.stage == "NONE"
    assert not new_item.normalized_word
    assert not new_item.sentence
    assert not new_item.translation


@allure.feature("Deck pipeline")
@allure.story("Task lifecycle")
async def test_task_with_partually_done_status_is_not_processing_again(
    pipeline: DeckPipeline, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PARTIALLY_DONE",
        current_stage="NONE",
        total_items=1,
        options={},
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_task.status == "PARTIALLY_DONE"
    assert new_item.status == "PENDING"
    assert new_item.stage == "NONE"
    assert not new_item.normalized_word
    assert not new_item.sentence
    assert not new_item.translation


@allure.feature("Deck pipeline")
@allure.story("Word normalization")
async def test_normalization_fills_in_normalized_word(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_normalizer,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={"normalization": True},
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="Dogs", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_item.normalized_word == "dogs"
    assert new_item.status == "DONE"
    assert new_item.status == "DONE"
    assert new_task.status == "DONE"
    assert fake_normalizer.calls == ["Dogs"]


@allure.feature("Deck pipeline")
@allure.story("Context generation")
async def test_context_generation_fills_in_sentence_and_translation(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    fake_anki,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={"limit": 1, "sentence_lang": "english", "translation_lang": "russian"},
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_item.sentence == "cat sentence"
    assert new_item.translation == "cat translation"
    assert new_item.status == "DONE"
    assert new_task.status == "DONE"
    assert len(fake_anki.cards) == 1
    assert fake_anki.exported_decks == [str(new_task.id)]
    assert fake_context_generator.calls == [
        {
            "word": "cat",
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        }
    ]


@allure.feature("Deck pipeline")
@allure.story("Context generation")
async def test_context_generator_uses_normalized_word(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    fake_normalizer,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={
            "normalization": True,
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="Dogs", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_item.normalized_word == "dogs"
    assert new_item.sentence == "dogs sentence"
    assert new_item.translation == "dogs translation"
    assert new_task.status == "DONE"
    assert fake_normalizer.calls == ["Dogs"]
    assert fake_context_generator.calls[0]["word"] == "dogs"


@allure.feature("Deck pipeline")
@allure.story("Batch item processing")
async def test_several_items_are_being_processed(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_normalizer,
    fake_anki,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=3,
        options={
            "normalization": True,
        },
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    items = [
        DeckItem(status="PENDING", stage="NONE", raw_word="Cats", task_id=task.id),
        DeckItem(status="PENDING", stage="NONE", raw_word="Dogs", task_id=task.id),
        DeckItem(status="PENDING", stage="NONE", raw_word="Books", task_id=task.id),
    ]
    db_session.add_all(items)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)

    new_items = (
        (await db_session.execute(select(DeckItem).where(DeckItem.task_id == task.id)))
        .scalars()
        .all()
    )

    for new_item in new_items:
        assert new_item.status == "DONE"
        assert new_item.normalized_word in {"cats", "dogs", "books"}

    assert len(fake_normalizer.calls) == 3
    assert len(fake_anki.exported_decks) == 3


@allure.feature("Deck pipeline")
@allure.story("Error handling")
async def test_external_service_error_on_one_item_makes_task_prtially_done(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    broken_item = DeckItem(
        status="PENDING", stage="NONE", raw_word="broken", task_id=task.id
    )
    db_session.add_all([item, broken_item])
    await db_session.commit()

    fake_context_generator.words_to_fail.add("broken")

    await pipeline.run(task.id)

    db_session.expire_all()

    await db_session.refresh(task)
    await db_session.refresh(item)
    await db_session.refresh(broken_item)

    cat = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()
    broken = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == broken_item.id))
    ).scalar_one()

    assert task.status == "PARTIALLY_DONE"
    assert cat.status == "DONE"
    assert broken.status == "ERROR"


@allure.feature("Deck pipeline")
@allure.story("Task lookup")
async def test_missing_task_id_raises_not_found_error(pipeline: DeckPipeline):
    missing_id = uuid.uuid4()

    with pytest.raises(NotFoundError):
        await pipeline.run(missing_id)


async def test_only_one_worker_can_claim_pending_task(
    decktask_service,
    test_user,
    db_session,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.commit()

    results = await asyncio.gather(
        decktask_service.claim_for_processing(task.id),
        decktask_service.claim_for_processing(task.id),
    )

    assert sorted(results) == [False, True]

    await db_session.refresh(task)
    assert task.status == "PROCESSING"


async def test_only_one_concurrent_pipeline_run_processes_task(
    pipeline: DeckPipeline,
    test_user,
    db_session,
    fake_normalizer,
    fake_context_generator,
    fake_anki,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        options={
            "normalization": True,
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
        user_id=test_user.id,
    )

    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await asyncio.gather(pipeline.run(task.id), pipeline.run(task.id))

    db_session.expire_all()
    await db_session.refresh(task)
    await db_session.refresh(item)

    new_task = (
        await db_session.execute(select(DeckTask).where(DeckTask.id == task.id))
    ).scalar_one()
    new_item = (
        await db_session.execute(select(DeckItem).where(DeckItem.id == item.id))
    ).scalar_one()

    assert new_task.status == "DONE"
    assert new_item.status == "DONE"
    assert len(fake_normalizer.calls) == 1
    assert len(fake_context_generator.calls) == 1
    assert len(fake_anki.exported_decks) == 1
