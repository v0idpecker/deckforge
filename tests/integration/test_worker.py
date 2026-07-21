import asyncio
import uuid

import allure
import pytest
from faststream.rabbit import RabbitBroker

pytestmark = pytest.mark.asyncio


async def wait_until(condition, timeout=3, interval=0.1):
    attempts = int(timeout / interval)

    for _ in range(attempts):
        if condition():
            return
        await asyncio.sleep(interval)


@allure.feature("Deck worker")
@allure.story("Task message handling")
async def test_worker_get_valid_task_id_and_calls_pipeline(
    faststream_app, broker: RabbitBroker, rabbit_config, fake_pipeline
):
    task_id = uuid.uuid4()

    await broker.publish(str(task_id), rabbit_config.rabbitmq.queue_name)

    await asyncio.wait_for(fake_pipeline.event.wait(), timeout=3)

    assert fake_pipeline.processed_task_ids == [task_id]


@allure.feature("Deck worker")
@allure.story("Task message handling")
async def test_worker_transmits_uuid(
    faststream_app, broker: RabbitBroker, rabbit_config, fake_pipeline
):
    task_id = uuid.uuid4()

    await broker.publish(str(task_id), rabbit_config.rabbitmq.queue_name)

    await asyncio.wait_for(fake_pipeline.event.wait(), timeout=3)

    assert fake_pipeline.processed_task_ids == [task_id]
    assert isinstance(fake_pipeline.processed_task_ids[0], uuid.UUID)


@allure.feature("Deck worker")
@allure.story("Task message handling")
async def test_worker_processes_multiple_messages(
    faststream_app, broker: RabbitBroker, rabbit_config, fake_pipeline
):
    task_1 = uuid.uuid4()
    task_2 = uuid.uuid4()
    task_3 = uuid.uuid4()

    await broker.publish(str(task_1), rabbit_config.rabbitmq.queue_name)
    await broker.publish(str(task_2), rabbit_config.rabbitmq.queue_name)
    await broker.publish(str(task_3), rabbit_config.rabbitmq.queue_name)

    await wait_until(lambda: len(fake_pipeline.processed_task_ids) == 3)
    assert set(fake_pipeline.processed_task_ids) == set((task_1, task_2, task_3))


@allure.feature("Deck worker")
@allure.story("Invalid messages")
async def test_invalid_uuid_doesnt_call_pipeline(
    faststream_app, broker: RabbitBroker, rabbit_config, fake_pipeline
):
    invalid_id = "not-uuid"

    await broker.publish(invalid_id, rabbit_config.rabbitmq.queue_name)

    await asyncio.sleep(0.2)

    assert fake_pipeline.processed_task_ids == []


@allure.feature("Deck worker")
@allure.story("Worker resilience")
async def test_pipeline_exception_doesnt_permanently_break_process(
    faststream_app, broker: RabbitBroker, rabbit_config, fake_pipeline
):
    failing_task_id = uuid.uuid4()
    successful_task_id = uuid.uuid4()

    fake_pipeline.fail_for_task_ids.add(failing_task_id)

    await broker.publish(str(failing_task_id), rabbit_config.rabbitmq.queue_name)
    await broker.publish(str(successful_task_id), rabbit_config.rabbitmq.queue_name)

    await wait_until(lambda: len(fake_pipeline.processed_task_ids) == 2)
    assert successful_task_id in fake_pipeline.processed_task_ids
    assert failing_task_id not in fake_pipeline.processed_task_ids
    assert failing_task_id in fake_pipeline.attempted_task_ids
