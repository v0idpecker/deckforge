from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.db.dao import DeckTaskDAO


class DeckTaskService:
    def __init__(self, session: AsyncSession, decktask_dao: DeckTaskDAO):
        self.session = session
        self.decktask_dao = decktask_dao
