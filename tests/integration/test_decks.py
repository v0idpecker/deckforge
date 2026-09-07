from pathlib import Path
from uuid import UUID, uuid4

import allure
import pytest
from httpx import AsyncClient, HTTPError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.db.models.decks import DeckCard, DeckItem, DeckTask
from deckforge.db.models.outbox import EventStatus, OutboxEvent
from deckforge.db.models.user import User
from deckforge.dto.user import UserDTO

pytestmark = pytest.mark.asyncio


@allure.feature("Decks API")
@allure.story("Create deck task")
async def test_create_deck_task_creates_task(
    client: AsyncClient,
    db_session: AsyncSession,
):
    response = await client.post(
        url="/api/decks/",
        json={
            "words": ["cat", "dog"],
            "options": {"normalization": True, "limit": 1},
        },
    )

    task_id = UUID(response.json()["task_id"])

    assert response.status_code == 200
    assert task_id

    res_task = await db_session.execute(select(DeckTask).where(DeckTask.id == task_id))
    task = res_task.scalar_one()

    res_event = await db_session.execute(select(OutboxEvent))
    event = res_event.scalar_one()

    assert task
    assert event.status == EventStatus.NEW
    assert event.event_type == "deck_task_requested"
    assert event.payload["task_id"] == str(task.id)


@allure.feature("Decks API")
@allure.story("Create deck task")
async def test_create_deck_task_creates_items(
    client: AsyncClient, db_session: AsyncSession
):
    response = await client.post(
        url="/api/decks/", json={"words": ["cat", "dog", "book"], "options": {}}
    )

    assert response.status_code == 200

    task_id = UUID(response.json()["task_id"])

    res = await db_session.execute(select(DeckItem).where(DeckItem.task_id == task_id))
    items = res.scalars().all()

    assert len(items) == 3
    assert items[0].raw_word == "cat"
    assert items[1].raw_word == "dog"
    assert items[2].raw_word == "book"
    for item in items:
        assert item.task_id == task_id


@allure.feature("Decks API")
@allure.story("Create deck task")
async def test_create_deck_task_creates_task_with_correct_state(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    response = await client.post(
        url="/api/decks/", json={"words": ["word"], "options": {}}
    )

    assert response.status_code == 200

    task_id = UUID(response.json()["task_id"])

    res = await db_session.execute(select(DeckTask).where(DeckTask.id == task_id))
    task = res.scalar_one()

    assert task.status == "PENDING"
    assert task.current_stage == "NONE"
    assert task.total_items == 1
    assert task.completed_items == 0
    assert task.failed_items == 0
    assert task.options == {}
    assert task.user_id == test_user.id


@allure.feature("Decks API")
@allure.story("Create deck task")
async def test_publisher_is_called_after_create_deck_task(client: AsyncClient):
    response = await client.post(
        url="/api/decks/", json={"words": ["word"], "options": {}}
    )
    assert response.status_code == 200


@allure.feature("Decks API")
@allure.story("List deck tasks")
async def test_get_decks_returns_current_user_data(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    another_user = User(
        email="another@example.com", name="another", google_id="another-google-id"
    )
    db_session.add(another_user)
    await db_session.flush()

    current_user_task_1 = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=test_user.id,
    )

    current_user_task_2 = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=3,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=test_user.id,
    )

    another_user_task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=another_user.id,
    )

    db_session.add_all([current_user_task_1, current_user_task_2, another_user_task])
    await db_session.commit()

    response = await client.get(url="/api/decks/")
    assert response.status_code == 200

    data = response.json()
    returned_ids = {item["id"] for item in data}

    assert returned_ids == {str(current_user_task_1.id), str(current_user_task_2.id)}
    assert str(another_user_task.id) not in returned_ids
    for item in data:
        assert set(item.keys()) == {"id", "status", "total_items"}


@allure.feature("Decks API")
@allure.story("List deck tasks")
async def test_get_decks_returns_empty_list(client: AsyncClient):
    response = await client.get(url="/api/decks/")

    assert response.status_code == 200
    assert response.json() == []


@allure.feature("Decks API")
@allure.story("Get deck status")
async def test_get_status_returns_task_status_and_all_items(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=2,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()

    item_1 = DeckItem(
        task_id=task.id,
        raw_word="cat",
        status="PENDING",
        stage="NONE",
    )
    item_2 = DeckItem(
        task_id=task.id,
        raw_word="dog",
        status="PROCESSING",
        stage="NORMALIZED",
    )
    db_session.add_all([item_1, item_2])
    await db_session.commit()

    response = await client.get(url=f"/api/decks/{task.id}/status")
    assert response.status_code == 200

    data = response.json()
    items_by_word = {item["raw_word"]: item for item in data["items"]}

    assert data["status"] == "PENDING"
    assert items_by_word["cat"]["status"] == "PENDING"
    assert items_by_word["dog"]["status"] == "PROCESSING"
    assert not items_by_word["cat"]["stage"]
    assert items_by_word["dog"]["stage"] == "NORMALIZED"


@allure.feature("Decks API")
@allure.story("Get deck status")
async def test_status_of_another_task_returns_403(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    another_user = User(
        email="another@example.com", name="another", google_id="another-google-id"
    )
    db_session.add(another_user)
    await db_session.flush()

    another_user_task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=another_user.id,
    )

    db_session.add(another_user_task)
    await db_session.commit()

    response = await client.get(url=f"/api/decks/{another_user_task.id}/status")

    data = response.json()
    assert response.status_code == 403
    assert data["detail"] == "Forbidden"


@allure.feature("Decks API")
@allure.story("Get deck status")
async def test_get_missing_task_status(client: AsyncClient):
    missing_uuid = uuid4()

    response = await client.get(url=f"/api/decks/{missing_uuid}/status")

    data = response.json()
    assert response.status_code == 404
    assert "not found" in data["detail"].lower()


@allure.feature("Decks API")
@allure.story("Get deck status")
async def test_uncorrect_uuid_in_path(client: AsyncClient):
    response = await client.get(url="/api/decks/uncorrect-uuid/status")

    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["type"]


@allure.feature("Decks API")
@allure.story("Download deck result")
async def test_result_without_file_returns_404(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.commit()

    response = await client.get(url=f"/api/decks/{task.id}/result")

    with pytest.raises(HTTPError):
        response.raise_for_status()
        assert response.status_code == 404


@allure.feature("Decks API")
@allure.story("Download deck result")
async def test_result_returns_existing_file(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.commit()

    media_dir = Path("media")
    media_dir.mkdir(exist_ok=True)

    deck_path = media_dir / f"{task.id}.apkg"
    deck_path.write_bytes(b"fake apkg content")

    try:
        response = await client.get(url=f"/api/decks/{task.id}/result")

        assert response.status_code == 200
        assert response.content == b"fake apkg content"
        assert response.headers["content-type"].startswith("application/octet-stream")

    finally:
        deck_path.unlink(missing_ok=True)


@allure.feature("Decks API")
@allure.story("Download deck result")
async def test_result_of_someone_else_task_returns_403(
    client: AsyncClient, db_session: AsyncSession
):
    another_user = User(
        email="another@example.com", name="another", google_id="another-google-id"
    )
    db_session.add(another_user)
    await db_session.flush()

    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=0,
        options={},
        user_id=another_user.id,
    )
    db_session.add(task)
    await db_session.commit()

    media_dir = Path("media")
    media_dir.mkdir(exist_ok=True)

    deck_path = media_dir / f"{task.id}.apkg"
    deck_path.write_bytes(b"fake apkg content")

    try:
        response = await client.get(url=f"/api/decks/{task.id}/result")
        assert response.status_code == 403
    finally:
        deck_path.unlink(missing_ok=True)


@allure.feature("Decks API")
@allure.story("Create deck task")
async def test_create_empty_deck_task(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(url="/api/decks/", json={"words": [], "options": {}})

    assert response.status_code == 200

    task_id = response.json()["task_id"]
    res = await db_session.execute(select(DeckTask).where(DeckTask.id == task_id))
    task = res.scalar_one()

    assert task.total_items == 0


@allure.feature("Decks API")
@allure.story("Get deck cards")
async def test_get_cards_for_task_without_cards_returns_empty_list(
    client: AsyncClient, db_session: AsyncSession, test_user: UserDTO
):
    task = DeckTask(
        status="PARTIALLY_DONE",
        current_stage="NONE",
        total_items=1,
        completed_items=0,
        failed_items=1,
        options={},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.commit()

    response = await client.get(url=f"/api/decks/{task.id}/cards")

    assert response.status_code == 200

    data = response.json()
    assert data["task_id"] == str(task.id)
    assert data["cards"] == []


@allure.feature("Deck pipeline")
@allure.story("Complete without cards after item failures")
async def test_pipeline_all_items_failed_completes_partially_done_without_retry(
    pipeline,
    fake_anki,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch: pytest.MonkeyPatch,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=2,
        completed_items=0,
        failed_items=0,
        options={"normalization": False, "limit": 1},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()

    item_1 = DeckItem(task_id=task.id, raw_word="cat", status="PENDING", stage="NONE")
    item_2 = DeckItem(task_id=task.id, raw_word="dog", status="PENDING", stage="NONE")
    db_session.add_all([item_1, item_2])
    await db_session.commit()

    # Захватываем id до expire_all: обращение к атрибуту expired-объекта
    # вне greenlet-контекста вызывает MissingGreenlet.
    task_id = task.id

    async def failing_context(item, *args, **kwargs):
        raise RuntimeError(f"no context for {item.raw_word}")

    monkeypatch.setattr(pipeline, "get_context_sentence", failing_context)

    await pipeline.run(task_id)

    db_session.expire_all()
    res_task = await db_session.execute(
        select(DeckTask).where(DeckTask.id == task_id)
    )
    updated_task = res_task.scalar_one()

    assert updated_task.status == "PARTIALLY_DONE"
    assert updated_task.attempt_count == 0
    assert updated_task.next_retry_at is None
    assert fake_anki.export_calls == []

    res_items = await db_session.execute(
        select(DeckItem).where(DeckItem.task_id == task_id)
    )
    items = res_items.scalars().all()
    assert len(items) == 2
    for item in items:
        assert item.status == "ERROR"
        assert item.error


@allure.feature("Deck pipeline")
@allure.story("Export cards with partial item failures")
async def test_pipeline_partial_failure_with_cards_exports_and_completes(
    pipeline,
    fake_anki,
    db_session: AsyncSession,
    test_user: UserDTO,
    monkeypatch: pytest.MonkeyPatch,
):
    task = DeckTask(
        status="PENDING",
        current_stage="NONE",
        total_items=2,
        completed_items=0,
        failed_items=0,
        options={"normalization": False, "limit": 1},
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.flush()

    item_cat = DeckItem(
        task_id=task.id, raw_word="cat", status="PENDING", stage="NONE"
    )
    item_dog = DeckItem(
        task_id=task.id, raw_word="dog", status="PENDING", stage="NONE"
    )
    db_session.add_all([item_cat, item_dog])
    await db_session.commit()

    # Захватываем id до expire_all: обращение к атрибуту expired-объекта
    # вне greenlet-контекста вызывает MissingGreenlet.
    task_id = task.id

    original_get_context = pipeline.get_context_sentence

    async def maybe_failing_context(item, *args, **kwargs):
        if item.raw_word == "dog":
            raise RuntimeError("no context for dog")
        return await original_get_context(item, *args, **kwargs)

    monkeypatch.setattr(pipeline, "get_context_sentence", maybe_failing_context)

    await pipeline.run(task_id)

    db_session.expire_all()
    res_task = await db_session.execute(
        select(DeckTask).where(DeckTask.id == task_id)
    )
    updated_task = res_task.scalar_one()

    assert updated_task.status == "PARTIALLY_DONE"

    assert len(fake_anki.export_calls) == 1
    exported_task_id, _, exported_cards = fake_anki.export_calls[0]
    assert exported_task_id == task_id
    assert [card.word for card in exported_cards] == ["cat"]

    res_items = await db_session.execute(
        select(DeckItem).where(DeckItem.task_id == task_id)
    )
    items_by_word = {item.raw_word: item for item in res_items.scalars().all()}
    assert items_by_word["cat"].status == "DONE"
    assert items_by_word["dog"].status == "ERROR"
    assert items_by_word["dog"].error

    res_cards = await db_session.execute(
        select(DeckCard).where(DeckCard.task_id == task_id)
    )
    cards = res_cards.scalars().all()
    assert {card.word for card in cards} == {"cat"}
