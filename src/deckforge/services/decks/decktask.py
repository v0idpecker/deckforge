from pathlib import Path
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.adapters.amqp.queue_publisher import QueuePublisher
from deckforge.db.dao.decks import DeckItemDAO, DeckTaskDAO
from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAOMultipleResultsError,
    DAONotFoundError,
)
from deckforge.services.dto import (
    DeckItemCreateDTO,
    DeckItemDTO,
    DeckTaskCreateDTO,
    DeckTaskDTO,
)
from deckforge.services.errors import (
    ConflictError,
    DataAccessError,
    InvalidInputError,
    MultipleResultsError,
    NotFoundError,
    ServiceError,
)


class DeckTaskService:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        deckitem_dao: DeckItemDAO,
        decktask_dao: DeckTaskDAO,
        publisher: QueuePublisher,
    ):
        self._sessionmaker = sessionmaker
        self._deckitem_dao = deckitem_dao
        self._decktask_dao = decktask_dao
        self._publisher = publisher

    async def create_task(self, dto: DeckTaskCreateDTO, user_id: UUID):
        try:
            async with self._sessionmaker() as session, session.begin():
                task = await self._decktask_dao.create(dto, user_id, session)
                for word in dto.words:
                    item_dto = DeckItemCreateDTO(task.id, word)
                    await self._deckitem_dao.create(item_dto, session)

            await self._publisher.send(str(task.id))

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
