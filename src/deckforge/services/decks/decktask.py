from pathlib import Path
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.adapters.amqp.queue_publisher import QueuePublisher
from deckforge.db.dao.decks import DeckTaskDAO
from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAOMultipleResultsError,
    DAONotFoundError,
)
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.dto import DeckItemCreateDTO, DeckTaskCreateDTO, DeckTaskDTO
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
        deckitem_service: DeckItemSerivce,
        decktask_dao: DeckTaskDAO,
        publisher: QueuePublisher,
    ):
        self._sessionmaker = sessionmaker
        self._deckitem_service = deckitem_service
        self._decktask_dao = decktask_dao
        self._publisher = publisher

    async def create_task(self, dto: DeckTaskCreateDTO, user_id: UUID):
        try:
            async with self._sessionmaker() as session, session.begin():
                task = await self._decktask_dao.create(dto, user_id, session)
                await session.flush()
                task_id = task.id

            for word in dto.words:
                item_dto = DeckItemCreateDTO(task_id, word)
                await self._deckitem_service.create_items(item_dto)

            await self._publisher.send(str(task_id))

            return task_id
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
