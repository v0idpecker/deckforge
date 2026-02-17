from uuid import UUID

from sqlalchemy.ext.asyncio.session import AsyncSession

from deckforge.db.dao import DeckItemDAO
from deckforge.services.dto import DeckItemCreateDTO, DeckItemDTO


class DeckItemSerivce:
    def __init__(self, deckitem_dao: DeckItemDAO):
        self._deckitem_dao = deckitem_dao

    async def create_items(self, session: AsyncSession, dto: DeckItemCreateDTO):
        await self._deckitem_dao.create(dto, session)

    async def get_task_items(self, session: AsyncSession, task_id: UUID):
        return await self._deckitem_dao.get_items_by_task_id(task_id, session)

    async def set_status(self, session: AsyncSession, id: UUID, status: str):
        await self._deckitem_dao.set_status(id, status, session)

    async def update_item(self, session: AsyncSession, dto: DeckItemDTO):
        await self._deckitem_dao.update_item(session, dto)
