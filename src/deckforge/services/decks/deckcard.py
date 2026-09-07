from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.db.dao.decks import DeckCardDAO
from deckforge.db.errors import DAOError
from deckforge.dto.deck_card import DeckCardCreateDTO, DeckCardDTO
from deckforge.services.errors import ServiceError


class DeckCardService:
    def __init__(
        self, deckcard_dao: DeckCardDAO, sessionmaker: async_sessionmaker[AsyncSession]
    ):
        self._deckcard_dao = deckcard_dao
        self._sessionmaker = sessionmaker

    async def replace_for_item(self, item_id: UUID, cards: List[DeckCardCreateDTO]):
        try:
            async with self._sessionmaker() as session, session.begin():
                await self._deckcard_dao.replace_for_item(session, item_id, cards)
        except DAOError as e:
            raise ServiceError(str(e))

    async def list_by_task(self, task_id: UUID) -> List[DeckCardDTO]:
        try:
            async with self._sessionmaker() as session, session.begin():
                return await self._deckcard_dao.list_by_task(session, task_id)
        except DAOError as e:
            raise ServiceError(str(e))
