from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.db.dao import DeckItemDAO
from deckforge.services.dto import DeckItemCreateDTO, DeckItemDTO


class DeckItemSerivce:
    def __init__(
        self, deckitem_dao: DeckItemDAO, sessionmaker: async_sessionmaker[AsyncSession]
    ):
        self._deckitem_dao = deckitem_dao
        self._sessionmaker = sessionmaker

    async def create_items(self, dto: DeckItemCreateDTO):
        async with self._sessionmaker() as session, session.begin():
            await self._deckitem_dao.create(dto, session)

    async def get_task_items(self, task_id: UUID):
        async with self._sessionmaker() as session, session.begin():
            return await self._deckitem_dao.get_items_by_task_id(task_id, session)

    async def update_item(self, dto: DeckItemDTO):
        async with self._sessionmaker() as session, session.begin():
            await self._deckitem_dao.update_item(session, dto)
