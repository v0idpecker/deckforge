from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.config import Config
from deckforge.db.dao import DeckItemDAO, DeckTaskDAO
from deckforge.db.sessionmaker import new_sessionmaker


class DBProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_sessionmaker(
        self, config: Config
    ) -> async_sessionmaker[AsyncSession]:
        return await new_sessionmaker(psql_config=config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session


class DAOProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_decktask_dao(self, session: AsyncSession) -> DeckTaskDAO:
        return DeckTaskDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def get_deckitem_dao(self, session: AsyncSession) -> DeckItemDAO:
        return DeckItemDAO(session=session)
