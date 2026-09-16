from typing import TYPE_CHECKING, AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit.broker import RabbitBroker
from nltk.stem.wordnet import WordNetLemmatizer
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ankislop.adapters.amqp.queue_publisher import RabbitPublisher
from ankislop.adapters.anki import AnkiAdapter
from ankislop.adapters.context_generator import ContextGenerator
from ankislop.adapters.normalizer import Normalizer
from ankislop.adapters.security import GoogleOAuthAdapter, JWTAdapter
from ankislop.config import Config
from ankislop.db.dao.decks import DeckCardDAO, DeckItemDAO, DeckTaskDAO
from ankislop.db.dao.llm_cache import LLMCacheDAO
from ankislop.db.dao.outbox import OutboxEventDAO
from ankislop.db.dao.user import UserDAO
from ankislop.db.sessionmaker import new_sessionmaker
from ankislop.pipeline.deck_pipeline import DeckPipeline
from ankislop.services.contextgen import ContextGenerationService
from ankislop.services.decks.deckcard import DeckCardService
from ankislop.services.decks.deckitem import DeckItemSerivce
from ankislop.services.decks.decktask import DeckTaskService
from ankislop.services.llm_cache import LLMCacheService
from ankislop.services.user import UserService

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
    decktask_dao = provide(DeckTaskDAO, scope=Scope.REQUEST)
    deckitem_dao = provide(DeckItemDAO, scope=Scope.REQUEST)
    deckcard_dao = provide(DeckCardDAO, scope=Scope.REQUEST)
    user_dao = provide(UserDAO, scope=Scope.REQUEST)
    outbox_event_dao = provide(OutboxEventDAO, scope=Scope.REQUEST)
    llm_cache_dao = provide(LLMCacheDAO, scope=Scope.REQUEST)

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
        sessionmaker: async_sessionmaker[AsyncSession],
        deckitem_dao: DeckItemDAO,
        decktask_dao: DeckTaskDAO,
        outbox_event_dao: OutboxEventDAO,
    ) -> DeckTaskService:
        return DeckTaskService(
            sessionmaker, deckitem_dao, decktask_dao, outbox_event_dao
        )

    @provide(scope=Scope.REQUEST)
    async def get_deckitem_service(
        self, sessionmaker: async_sessionmaker[AsyncSession], deckitem_dao: DeckItemDAO
    ) -> DeckItemSerivce:
        return DeckItemSerivce(deckitem_dao, sessionmaker)

    @provide(scope=Scope.REQUEST)
    async def get_user_service(
        self, sessionmaker: async_sessionmaker[AsyncSession], user_dao: UserDAO
    ) -> UserService:
        return UserService(sessionmaker, user_dao)

    @provide(scope=Scope.REQUEST)
    async def get_deckcard_service(
        self, sessionmaker: async_sessionmaker[AsyncSession], deckcard_dao: DeckCardDAO
    ) -> DeckCardService:
        return DeckCardService(deckcard_dao, sessionmaker)

    @provide(scope=Scope.REQUEST)
    async def get_cache_service(
        self, sessionmaker: async_sessionmaker[AsyncSession], cache_dao: LLMCacheDAO
    ) -> LLMCacheService:
        return LLMCacheService(sessionmaker, cache_dao)

    @provide(scope=Scope.REQUEST)
    async def get_contextgen_service(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        generator: ContextGenerator,
        cache_service: LLMCacheService,
    ) -> ContextGenerationService:
        return ContextGenerationService(sessionmaker, generator, cache_service)

class PipelineProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_deck_pipeline(
        self,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
        deckcard_service: DeckCardService,
        normalizer: Normalizer,
        context_generator: ContextGenerationService,
        anki: AnkiAdapter,
        config: Config,
    ) -> DeckPipeline:
        return DeckPipeline(
            decktask_service,
            deckitem_service,
            deckcard_service,
            normalizer,
            context_generator,
            anki,
            config.asyncio.concurrency,
        )

class WordProcessingProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    lemmatizer = provide(WordNetLemmatizer, scope=Scope.REQUEST)
    anki = provide(AnkiAdapter, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_normalizer(self, lemmatizer: WordNetLemmatizer) -> Normalizer:
        return Normalizer(lemmatizer)

    @provide(scope=Scope.REQUEST)
    async def get_context_generator(
        self, client: AsyncOpenAI, config: Config
    ) -> ContextGenerator:
        return ContextGenerator(client=client, model=config.llm.model)

    @provide(scope=Scope.APP)
    async def get_llm_client(self, config: Config) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=config.llm.api_key.get_secret_value(), base_url=config.llm.base_url
        )

class SecurityProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_oauth_adapter(self, config: Config) -> GoogleOAuthAdapter:
        return GoogleOAuthAdapter(config.security)

    @provide(scope=Scope.REQUEST)
    async def get_jwt_adapter(self, config: Config) -> JWTAdapter:
        return JWTAdapter(config.security)

class HTTPProvder(Provider):
    if TYPE_CHECKING:
        from httpx import AsyncClient

        client = provide(AsyncClient, scope=Scope.APP)
