from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.db.dao import DeckItemDAO


class DeckItemSerivce:
    def __init__(self, session: AsyncSession, deckitem_dao: DeckItemDAO):
        self._session = session
        self._deckitem_dao = deckitem_dao
