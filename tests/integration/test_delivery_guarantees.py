import asyncio
from datetime import datetime, timedelta

import allure
import pytest
from sqlalchemy import update

from deckforge.db.models.decks import DeckTask
from deckforge.dto.deck_task import DeckTaskCreateDTO
from deckforge.relay.service import OutboxRelay
from deckforge.scheduler.service import RetryScheduler
from deckforge.services.errors import DataAccessError

pytestmark = pytest.mark.asyncio

async def wait_until(condition, timeout=3, interval=0.1):
    deadline = datetime.now() + timedelta(seconds=timeout)
    while datetime.now() < deadline:
        if await condition():
            return
        await asyncio.sleep(interval)
    raise TimeoutError("condition was not met in time")

def make_create_dto() -> DeckTaskCreateDTO:
    return DeckTaskCreateDTO(
        words=["reliability"],
        options={
            "limit": 1,
            "sentence_lang": "english",
            "translation_lang": "russian",
            "difficulty": "B1",
        },
    )

@allure.feature("Outbox")
@allure.story("два параллельных relay публикуют событие один раз")
async def test_process_batch_publishes_event_once_under_concurrency(
    sessionmaker, outbox_dao, fake_publisher, decktask_service, test_user
):
    task_id = await decktask_service.create_task(make_create_dto(), test_user.id)

    relay_a = OutboxRelay(sessionmaker, outbox_dao, fake_publisher)
    relay_b = OutboxRelay(sessionmaker, outbox_dao, fake_publisher)

    processed_a, processed_b = await asyncio.gather(
        relay_a.process_batch(), relay_b.process_batch()
    )

    assert processed_a + processed_b == 1
    assert fake_publisher.messages == [str(task_id)]

    processed_again = await relay_a.process_batch()
    assert processed_again == 0
    assert fake_publisher.messages == [str(task_id)]

@allure.feature("Scheduler")
@allure.story("два параллельных tick создают одно outbox-событие на задачу")
async def test_concurrent_ticks_create_single_outbox_event_per_task(
    sessionmaker, outbox_dao, decktask_service, test_user, db_session
):
    task_id = await decktask_service.create_task(make_create_dto(), test_user.id)
    await decktask_service.mark_for_retry_or_fail(task_id, RuntimeError("boom"))

    await db_session.execute(
        update(DeckTask)
        .where(DeckTask.id == task_id)
        .values(next_retry_at=datetime.now() - timedelta(seconds=1))
    )
    await db_session.commit()

    events_before = {
        e.id
        for e in await outbox_dao.list(db_session)
        if e.payload.get("task_id") == str(task_id)
    }

    scheduler_a = RetryScheduler(
        decktask_service,
        sessionmaker,
        outbox_dao,
        task_timeout_base=10,
        task_timeout_per_item=5,
    )
    scheduler_b = RetryScheduler(
        decktask_service,
        sessionmaker,
        outbox_dao,
        task_timeout_base=10,
        task_timeout_per_item=5,
    )

    await asyncio.gather(scheduler_a.tick(), scheduler_b.tick())

    events = await outbox_dao.list(db_session)
    new_task_events = [
        e
        for e in events
        if e.id not in events_before and e.payload.get("task_id") == str(task_id)
    ]
    assert len(new_task_events) == 1

    task = await decktask_service.get_task(task_id)
    assert task.status == "PENDING"

@allure.feature("Worker")
@allure.story("падение mark_for_retry_or_fail сохраняет статус задачи и переотправляет сообщение")
async def test_worker_keeps_task_status_when_retry_marking_fails(
    faststream_app,
    publisher,
    fake_pipeline,
    fake_task_service,
    decktask_service,
    test_user,
    db_session,
):
    task_id = await decktask_service.create_task(make_create_dto(), test_user.id)
    await db_session.execute(
        update(DeckTask)
        .where(DeckTask.id == task_id)
        .values(status="PROCESSING")
    )
    await db_session.commit()

    fake_pipeline.fail_for_task_ids.add(task_id)

    async def failing_mark_for_retry_or_fail(retry_task_id, error):
        raise DataAccessError("service is down")

    fake_task_service.mark_for_retry_or_fail = failing_mark_for_retry_or_fail

    await publisher.send(str(task_id))

    async def redelivered():
        return len(fake_pipeline.attempted_task_ids) >= 2

    await wait_until(redelivered)

    assert fake_task_service.retried == []

    db_session.expire_all()
    task = await decktask_service.get_task(task_id)
    assert task.status == "PROCESSING"
