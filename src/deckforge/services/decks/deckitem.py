from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.db.dao.decks import DeckItemDAO
from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAONotFoundError,
)
from deckforge.services.dto import DeckItemCreateDTO, DeckItemDTO
from deckforge.services.errors import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    ServiceError,
)


class DeckItemSerivce:
    def __init__(
        self, deckitem_dao: DeckItemDAO, sessionmaker: async_sessionmaker[AsyncSession]
    ):
        self._deckitem_dao = deckitem_dao
        self._sessionmaker = sessionmaker

    async def create_items(self, dto: DeckItemCreateDTO):
        try:
            async with self._sessionmaker() as session, session.begin():
                await self._deckitem_dao.create(dto, session)
        except DAOInvalidInputError as e:
            raise InvalidInputError(str(e)) from e
        except DAOIntegrityError as e:
            raise ConflictError(str(e)) from e
        except DAOError as e:
            raise ServiceError(str(e)) from e

    async def get_task_items(self, task_id: UUID):
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._deckitem_dao.get_items_by_task_id(task_id, session)
            except DAONotFoundError as e:
                raise NotFoundError(f"Service error: {e}")
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def update_item(self, dto: DeckItemDTO):
        try:
            async with self._sessionmaker() as session, session.begin():
                await self._deckitem_dao.update(session, dto)
        except DAOError as e:
            raise ServiceError(str(e)) from e
