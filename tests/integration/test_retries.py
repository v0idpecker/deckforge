import datetime

import allure
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.adapters.errors import ExternalServiceError
from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.db.models.outbox import EventStatus, OutboxEvent
from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.scheduler.service import RetryScheduler
from deckforge.services.dto import UserDTO

pytestmark = pytest.mark.asyncio


class FixedDateTime(datetime.datetime):
    """Deterministic clock used instead of datetime.now() in retry logic."""

    current = datetime.datetime(2025, 6, 1, 12, 0, 0)

    @classmethod
    def now(cls, tz=None):
        return cls(
            cls.current.year,
            cls.current.month,
            cls.current.day,
            cls.current.hour,
            cls.current.minute,
            cls.current.second,
            cls.current.microsecond,
        )


def freeze_time(monkeypatch):
    FixedDateTime.current = datetime.datetime(2025, 6, 1, 12, 0, 0)
    monkeypatch.setattr("deckforge.services.decks.decktask.datetime", FixedDateTime)


def advance_time(**kwargs):
    FixedDateTime.current = FixedDateTime.current + datetime.timedelta(**kwargs)


def make_task(status: str, user_id, **kwargs) -> DeckTask:
    defaults = dict(
        current_stage="NONE",
        total_items=1,
        options={},
    )
    defaults.update(kwargs)
    return DeckTask(status=status, user_id=user_id, **defaults)


@allure.feature("Retries")
@allure.story("Retry scheduling")
async def test_first_error_schedules_retry(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)

    task = make_task(status="PROCESSING", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()

    await decktask_service.mark_for_retry_or_fail(task.id, RuntimeError("boom"))

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "RETRY_SCHEDULED"
    assert task.attempt_count == 1
    assert task.error == "boom"
    assert task.next_retry_at == FixedDateTime(2025, 6, 1, 12, 0, 2)


@allure.feature("Retries")
@allure.story("Retry scheduling")
async def test_backoff_grows_exponentially(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)

    task = make_task(status="PROCESSING", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()

    await decktask_service.mark_for_retry_or_fail(task.id, RuntimeError("first"))
    await decktask_service.mark_for_retry_or_fail(task.id, RuntimeError("second"))

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.attempt_count == 2
    assert task.next_retry_at == FixedDateTime(2025, 6, 1, 12, 0, 4)


@allure.feature("Retries")
@allure.story("Retry scheduling")
async def test_task_fails_after_max_attempts(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)

    task = make_task(status="PROCESSING", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()

    for i in range(4):
        await decktask_service.mark_for_retry_or_fail(
            task.id, RuntimeError(f"error-{i}")
        )

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "FAILED"
    assert task.attempt_count == 3
    assert task.error == "error-3"
    assert task.next_retry_at == FixedDateTime(2025, 6, 1, 12, 0, 8)


@allure.feature("Retries")
@allure.story("Retry scheduling")
async def test_mark_for_retry_does_not_touch_finished_task(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
):
    task = make_task(status="DONE", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()

    await decktask_service.mark_for_retry_or_fail(task.id, RuntimeError("boom"))

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "DONE"
    assert task.attempt_count == 0


@allure.feature("Retries")
@allure.story("Retry queue")
async def test_find_ready_for_retry_returns_only_due_tasks(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)
    now = FixedDateTime(2025, 6, 1, 12, 0, 0)

    due = make_task(
        status="RETRY_SCHEDULED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
    )
    not_yet = make_task(
        status="RETRY_SCHEDULED",
        user_id=test_user.id,
        next_retry_at=now + datetime.timedelta(hours=1),
    )
    failed = make_task(
        status="FAILED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
    )
    db_session.add_all([due, not_yet, failed])
    await db_session.commit()

    ready = await decktask_service.find_ready_for_retry()

    assert [task.id for task in ready] == [due.id]


@allure.feature("Retries")
@allure.story("Concurrency")
async def test_claim_returns_false_when_task_is_not_pending(
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
):
    task = make_task(status="PROCESSING", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()

    claimed = await decktask_service.claim_for_processing(task.id)

    assert claimed is False
    await db_session.refresh(task)
    assert task.status == "PROCESSING"


@allure.feature("Retries")
@allure.story("Scheduler")
async def test_tick_requeues_due_task_and_creates_single_event(
    scheduler: RetryScheduler,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)
    now = FixedDateTime(2025, 6, 1, 12, 0, 0)

    task = make_task(
        status="RETRY_SCHEDULED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
    )
    db_session.add(task)
    await db_session.commit()

    await scheduler.tick()

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "PENDING"

    events = (await db_session.execute(select(OutboxEvent))).scalars().all()
    assert len(events) == 1
    assert events[0].event_type == "deck_task_requested"
    assert events[0].payload["task_id"] == str(task.id)
    assert events[0].status == EventStatus.NEW


@allure.feature("Retries")
@allure.story("Scheduler")
async def test_tick_is_idempotent_for_requeued_task(
    scheduler: RetryScheduler,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)
    now = FixedDateTime(2025, 6, 1, 12, 0, 0)

    task = make_task(
        status="RETRY_SCHEDULED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
    )
    db_session.add(task)
    await db_session.commit()

    await scheduler.tick()
    await scheduler.tick()

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "PENDING"

    events = (await db_session.execute(select(OutboxEvent))).scalars().all()
    assert len(events) == 1


@allure.feature("Retries")
@allure.story("Scheduler")
async def test_failed_task_is_not_requeued(
    scheduler: RetryScheduler,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch,
):
    freeze_time(monkeypatch)
    now = FixedDateTime(2025, 6, 1, 12, 0, 0)

    task = make_task(
        status="FAILED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
    )
    db_session.add(task)
    await db_session.commit()

    await scheduler.tick()

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "FAILED"

    events = (await db_session.execute(select(OutboxEvent))).scalars().all()
    assert events == []


@allure.feature("Retries")
@allure.story("Worker contract")
async def test_pipeline_failure_schedules_retry(
    pipeline: DeckPipeline,
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    monkeypatch,
):
    freeze_time(monkeypatch)

    task = make_task(
        status="PENDING",
        user_id=test_user.id,
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
    )
    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    fake_context_generator.words_to_fail.add("cat")

    with pytest.raises(ExternalServiceError):
        await pipeline.run(task.id)

    # то же самое делает воркер при ошибке пайплайна (worker.py)
    await decktask_service.mark_for_retry_or_fail(
        task.id, ExternalServiceError("context service failed")
    )

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "RETRY_SCHEDULED"
    assert task.attempt_count == 1


@allure.feature("Retries")
@allure.story("Retry lifecycle")
async def test_retry_reprocesses_error_items(
    scheduler: RetryScheduler,
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    monkeypatch,
):
    freeze_time(monkeypatch)
    now = FixedDateTime(2025, 6, 1, 12, 0, 0)

    task = make_task(
        status="RETRY_SCHEDULED",
        user_id=test_user.id,
        next_retry_at=now - datetime.timedelta(minutes=1),
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
    )
    db_session.add(task)
    await db_session.flush()
    broken = DeckItem(status="ERROR", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(broken)
    await db_session.commit()

    await scheduler.tick()
    await pipeline.run(task.id)

    db_session.expire_all()
    await db_session.refresh(task)
    await db_session.refresh(broken)

    assert broken.status == "DONE"
    assert task.status == "DONE"


@allure.feature("Retries")
@allure.story("Retry lifecycle")
async def test_full_retry_cycle_failure_then_success(
    scheduler: RetryScheduler,
    pipeline: DeckPipeline,
    decktask_service,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    fake_anki,
    monkeypatch,
):
    freeze_time(monkeypatch)

    task = make_task(
        status="PENDING",
        user_id=test_user.id,
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
    )
    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    fake_context_generator.words_to_fail.add("cat")

    with pytest.raises(ExternalServiceError):
        await pipeline.run(task.id)

    await decktask_service.mark_for_retry_or_fail(
        task.id, ExternalServiceError("context service failed")
    )
    advance_time(seconds=10)
    await scheduler.tick()

    db_session.expire_all()
    await db_session.refresh(task)
    assert task.status == "PENDING"

    fake_context_generator.words_to_fail.clear()
    await pipeline.run(task.id)

    db_session.expire_all()
    await db_session.refresh(task)
    await db_session.refresh(item)

    assert task.status == "DONE"
    assert item.status == "DONE"
    assert task.attempt_count == 0
    assert task.next_retry_at is None


@allure.feature("Retries")
@allure.story("Retry lifecycle")
async def test_successful_run_resets_retry_counters(
    pipeline: DeckPipeline,
    db_session: AsyncSession,
    test_user: UserDTO,
    fake_context_generator,
    fake_anki,
):
    task = make_task(
        status="PENDING",
        user_id=test_user.id,
        attempt_count=2,
        next_retry_at=datetime.datetime(2025, 1, 1, 12, 0, 0),
        error="previous error",
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
        },
    )
    db_session.add(task)
    await db_session.flush()
    item = DeckItem(status="PENDING", stage="NONE", raw_word="cat", task_id=task.id)
    db_session.add(item)
    await db_session.commit()

    await pipeline.run(task.id)

    db_session.expire_all()
    await db_session.refresh(task)

    assert task.status == "DONE"
    assert task.attempt_count == 0
    assert task.next_retry_at is None
    assert task.error is None
