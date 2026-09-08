from datetime import datetime
from pathlib import Path
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.db.dao.decks import DeckItemDAO, DeckTaskDAO
from deckforge.db.dao.outbox import OutboxEventDAO
from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAOMultipleResultsError,
    DAONotFoundError,
)
from deckforge.dto.deck_item import DeckItemCreateDTO, DeckItemDTO
from deckforge.dto.deck_task import DeckTaskCreateDTO, DeckTaskDTO
from deckforge.dto.outbox_event import OutboxEventCreateDTO
from deckforge.services.errors import (
    ConflictError,
    DataAccessError,
    InvalidInputError,
    MultipleResultsError,
    NotFoundError,
    ServiceError,
)

MAX_ATTEMPTS = 3

class DeckTaskService:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        deckitem_dao: DeckItemDAO,
        decktask_dao: DeckTaskDAO,
        outbox_event_dao: OutboxEventDAO,
    ):
        self._sessionmaker = sessionmaker
        self._deckitem_dao = deckitem_dao
        self._decktask_dao = decktask_dao
        self._outbox_event_dao = outbox_event_dao

    @staticmethod
    def derive_deck_name(options: dict) -> str:
        return f"DeckForge::{options.get('sentence_lang', 'english')}→{options.get('translation_lang', 'russian')}"

    async def create_task(self, dto: DeckTaskCreateDTO, user_id: UUID):
        try:
            async with self._sessionmaker() as session, session.begin():
                task = await self._decktask_dao.create(dto, user_id, session)
                for word in dto.words:
                    item_dto = DeckItemCreateDTO(task.id, word)
                    await self._deckitem_dao.create(item_dto, session)
                event = OutboxEventCreateDTO(
                    payload={"task_id": str(task.id)}, event_type="deck_task_requested"
                )
                await self._outbox_event_dao.create(event, session)

            return task.id
        except DAOInvalidInputError as e:
            raise InvalidInputError(str(e)) from e
        except DAOIntegrityError as e:
            raise ConflictError(str(e)) from e
        except DAOError as e:
            raise DataAccessError(str(e)) from e

    async def get_task(self, task_id: UUID) -> DeckTaskDTO:
        async with self._sessionmaker() as session, session.begin():
            try:
                task = await self._decktask_dao.get(task_id, session)
                return task
            except DAONotFoundError as e:
                raise NotFoundError(str(e)) from e
            except DAOMultipleResultsError as e:
                raise MultipleResultsError(str(e)) from e
            except DAOError as e:
                raise DataAccessError(str(e)) from e

    async def get_task_items(self, task_id: UUID) -> List[DeckItemDTO]:
        async with self._sessionmaker() as session, session.begin():
            try:
                items = await self._deckitem_dao.get_all_items_by_task_id(
                    task_id, session
                )
                return items
            except DAOError as e:
                raise DataAccessError(str(e)) from e

    async def get_tasks(self, user_id: UUID) -> List[DeckTaskDTO]:
        async with self._sessionmaker() as session, session.begin():
            try:
                tasks = await self._decktask_dao.get_by_user(user_id, session)
                return tasks
            except DAONotFoundError as e:
                raise NotFoundError(str(e)) from e
            except DAOError as e:
                raise DataAccessError(str(e)) from e

    async def update_task_status(self, task_id: UUID, status: str):
        async with self._sessionmaker() as session, session.begin():
            try:
                await self._decktask_dao.update_status(session, task_id, status)
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def get_result_path(self, task_id: UUID) -> Path:
        deck_path = Path("media") / f"{task_id}.apkg"
        if not deck_path.is_file():
            raise NotFoundError("Deck file is not ready yet")
        return deck_path

    async def claim_for_processing(self, task_id: UUID) -> bool:
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._decktask_dao.claim_for_processing(task_id, session)
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def update_task(self, new_task: DeckTaskDTO):
        async with self._sessionmaker() as session, session.begin():
            try:
                await self._decktask_dao.update(new_task, session)
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def mark_for_retry_or_fail(
        self, task_id: UUID, error: Exception
    ) -> tuple[str, int] | None:
        try:
            async with self._sessionmaker() as session, session.begin():
                return await self._decktask_dao.schedule_retry_or_fail(
                    session,
                    task_id=task_id,
                    now=datetime.now(),
                    error=str(error),
                    max_attempts=MAX_ATTEMPTS,
                )
        except DAOError as e:
            raise ServiceError(str(e)) from e

    async def find_ready_for_retry(self) -> List[DeckTaskDTO]:
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._decktask_dao.get_tasks_ready_for_retry(
                    session, datetime.now()
                )
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def find_stale_processing_tasks(
        self, older_than: datetime
    ) -> List[DeckTaskDTO]:
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._decktask_dao.get_stale_processing_tasks(
                    session, older_than
                )
            except DAOError as e:
                raise DataAccessError(str(e)) from e

    async def reschedule_for_retry(self, task_id: UUID) -> bool:
        async with self._sessionmaker() as session, session.begin():
            try:
                claimed = await self._decktask_dao.claim_for_reschedule(
                    task_id, session
                )
                if not claimed:
                    return False
                event = OutboxEventCreateDTO(
                    payload={"task_id": str(task_id)}, event_type="deck_task_requested"
                )
                await self._outbox_event_dao.create(event, session)
                return True
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def complete_task(self, task_id: UUID, status: str):
        async with self._sessionmaker() as session, session.begin():
            try:
                await self._decktask_dao.complete(session, task_id, status)
            except DAOError as e:
                raise ServiceError(str(e)) from e
