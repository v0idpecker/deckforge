from uuid import UUID

from sqlalchemy.ext.asyncio.session import AsyncSession

from deckforge.db.dao import DeckItemDAO
from deckforge.services.dto import DeckItemCreateDTO


class DeckItemSerivce:
    def __init__(self, deckitem_dao: DeckItemDAO):
        self._deckitem_dao = deckitem_dao

    async def create_items(self, session: AsyncSession, dto: DeckItemCreateDTO):
        await self._deckitem_dao.create(dto, session)

    async def get_task_items(self, session: AsyncSession, task_id: UUID):
        await self._deckitem_dao.get_items_by_task_id(task_id, session)
