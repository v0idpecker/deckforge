from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit.broker import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.adapters.amqp.queue_publisher import RabbitPublisher
from deckforge.config import Config
from deckforge.db.dao import DeckItemDAO, DeckTaskDAO
from deckforge.db.sessionmaker import new_sessionmaker
from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService


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
    async def get_decktask_dao(self) -> DeckTaskDAO:
        return DeckTaskDAO()

    @provide(scope=Scope.REQUEST)
    async def get_deckitem_dao(self) -> DeckItemDAO:
        return DeckItemDAO()


class AMQPProvider(Provider):
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_publisher(
        self, broker: RabbitBroker, config: Config
    ) -> RabbitPublisher:
        return RabbitPublisher(broker, config.rabbitmq.queue_name)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_decktask_service(
        self,
        session: AsyncSession,
        deckitem_service: DeckItemSerivce,
        decktask_dao: DeckTaskDAO,
        publisher: RabbitPublisher,
    ) -> DeckTaskService:
        return DeckTaskService(session, deckitem_service, decktask_dao, publisher)

    @provide(scope=Scope.REQUEST)
    async def get_deckitem_service(self, deckitem_dao: DeckItemDAO) -> DeckItemSerivce:
        return DeckItemSerivce(deckitem_dao)


class PipelineProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_deck_pipeline(
        self,
        session: AsyncSession,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
    ) -> DeckPipeline:
        return DeckPipeline(session, decktask_service, deckitem_service)
