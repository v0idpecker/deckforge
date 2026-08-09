import asyncio
import uuid
from typing import AsyncIterable
from uuid import UUID

import httpx
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from faststream.app import FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from deckforge.adapters.amqp.queue_publisher import RabbitPublisher
from deckforge.adapters.amqp.worker import setup_worker
from deckforge.adapters.errors import ExternalServiceError
from deckforge.adapters.security import GoogleOAuthAdapter, JWTAdapter
from deckforge.api.handlers.auth import get_current_user
from deckforge.api.handlers.auth import router as auth_router
from deckforge.api.handlers.decks import router as decks_router
from deckforge.config import (
    AppConfig,
    Config,
    PostgresConfig,
    RabbitMQConfig,
    SecurityConfig,
)
from deckforge.db.dao.decks import DeckCardDAO, DeckItemDAO, DeckTaskDAO
from deckforge.db.dao.outbox import OutboxEventDAO
from deckforge.db.models import Base
from deckforge.db.models.user import User
from deckforge.di.providers import DAOProvider, ServiceProvider
from deckforge.dto.user import UserDTO
from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.scheduler.service import RetryScheduler
from deckforge.services.decks.deckcard import DeckCardService
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService

# base test fixtures


class TestDBProvider(Provider):
    def __init__(self, sessionmaker):
        super().__init__()
        self._sessionmaker = sessionmaker

    @provide(scope=Scope.APP)
    async def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self._sessionmaker

    @provide(scope=Scope.REQUEST)
    async def session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session


class TestPublisherProvider(Provider):
    def __init__(self, publisher):
        super().__init__()
        self._publisher = publisher

    @provide(scope=Scope.REQUEST)
    async def get_publisher(self) -> RabbitPublisher:
        return self._publisher


class FakePublisher(RabbitPublisher):
    def __init__(self):
        self.messages = []

    async def send(self, msg: str):
        self.messages.append(msg)


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        url="postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def sessionmaker(engine):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def db_session(sessionmaker):
    async with sessionmaker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def fake_publisher():
    return FakePublisher()


@pytest_asyncio.fixture
async def container(sessionmaker, fake_publisher):
    container = make_async_container(
        TestDBProvider(sessionmaker),
        DAOProvider(),
        ServiceProvider(),
        TestPublisherProvider(fake_publisher),
    )
    yield container

    await container.close()


@pytest_asyncio.fixture
async def test_user(db_session) -> UserDTO:
    user = User(email="user@example.com", name="test-user", google_id="google-test-id")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return UserDTO.from_entity(user)


@pytest_asyncio.fixture
async def app(container, test_user):
    app = FastAPI()
    app.include_router(decks_router)

    async def override_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_current_user

    setup_dishka(container=container, app=app)

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# auth test fixtures


@pytest_asyncio.fixture
async def test_config():
    return Config(
        postgres=PostgresConfig(
            url="postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
        ),
        rabbitmq=RabbitMQConfig(url="amqp://fake", queue_name="fake"),
        security=SecurityConfig(
            google_client_id="fake-client-id",
            google_client_secret="fake-client-secret",
            jwt_secret="test-jwt-secret",
            session_secret="test-session-secret",
        ),
        app=AppConfig(
            backend_public_url="http://test",
            frontend_url="http://frontend.test",
            cors_origins=["http://frontend.test"],
        ),
    )


class FakeGoogleOAuthAdatper(GoogleOAuthAdapter):
    def __init__(self):
        self.token = {
            "userinfo": {
                "sub": "google-user-id",
                "email": "user@example.com",
                "name": "Test User",
            }
        }
        self.authorize_error = None

    async def authorize_access_token(self, request):
        if self.authorize_error:
            raise self.authorize_error
        return self.token

    async def get_google_redirect(self, request, redirect_uri: str):
        return RedirectResponse(
            url=f"https://google.test/oauth?redirect_uri={redirect_uri}"
        )


class TestAuthProvider(Provider):
    def __init__(self, config: Config, oauth: GoogleOAuthAdapter):
        super().__init__()
        self._config = config
        self._oauth = oauth

    @provide(scope=Scope.APP)
    async def get_config(self) -> Config:
        return self._config

    @provide(scope=Scope.REQUEST)
    async def get_oauth_adapter(self) -> GoogleOAuthAdapter:
        return self._oauth

    @provide(scope=Scope.REQUEST)
    async def get_jwt_adapter(self) -> JWTAdapter:
        return JWTAdapter(self._config.security)


@pytest_asyncio.fixture
async def jwt_adapter(test_config):
    return JWTAdapter(test_config.security)


@pytest_asyncio.fixture
async def fake_oauth():
    return FakeGoogleOAuthAdatper()


@pytest_asyncio.fixture
async def auth_provider(test_config, fake_oauth):
    return TestAuthProvider(test_config, fake_oauth)


@pytest_asyncio.fixture
async def auth_container(sessionmaker, fake_publisher, test_config, fake_oauth):
    container = make_async_container(
        TestDBProvider(sessionmaker),
        DAOProvider(),
        ServiceProvider(),
        TestPublisherProvider(fake_publisher),
        TestAuthProvider(test_config, fake_oauth),
    )
    yield container

    await container.close()


@pytest_asyncio.fixture
async def auth_app(auth_container):
    app = FastAPI()
    app.include_router(decks_router)
    app.include_router(auth_router)

    setup_dishka(container=auth_container, app=app)

    yield app


@pytest_asyncio.fixture
async def auth_client(auth_app):
    transport = httpx.ASGITransport(app=auth_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# pipeline test fixtures


class FakeNormalizer:
    def __init__(self) -> None:
        self.calls = []

    def lemmatize_word(self, word: str):
        self.calls.append(word)
        return word.lower()


class FakeContextGenerator:
    def __init__(self) -> None:
        self.calls = []
        self.words_to_fail = set()

    async def get_context_sentence(
        self,
        word: str | None,
        limit: int,
        sentence_lang: str,
        translation_lang: str,
        difficulty: str,
    ):
        self.calls.append(
            {
                "word": word,
                "limit": limit,
                "sentence_lang": sentence_lang,
                "translation_lang": translation_lang,
                "difficulty": difficulty,
            }
        )

        if word in self.words_to_fail:
            raise ExternalServiceError("context service failed")

        return [
            {
                sentence_lang: f"{word} sentence",
                translation_lang: f"{word} translation",
            }
            for _ in range(limit)
        ]


class FakeAnki:
    def __init__(self):
        self.cards = []
        self.exported_decks = []

    def add_card(self, front, back):
        self.cards.append((front, back))

    def export_deck(self, deck_name):
        self.exported_decks.append(deck_name)


@pytest_asyncio.fixture
async def decktask_dao():
    return DeckTaskDAO()


@pytest_asyncio.fixture
async def deckitem_dao():
    return DeckItemDAO()


@pytest_asyncio.fixture
async def deckitem_service(deckitem_dao, sessionmaker):
    return DeckItemSerivce(deckitem_dao, sessionmaker)


@pytest_asyncio.fixture
async def deckcard_dao():
    return DeckCardDAO()


@pytest_asyncio.fixture
async def deckcard_service(deckcard_dao, sessionmaker):
    return DeckCardService(deckcard_dao, sessionmaker)


@pytest_asyncio.fixture
async def outbox_dao():
    return OutboxEventDAO()


@pytest_asyncio.fixture
async def decktask_service(sessionmaker, deckitem_dao, decktask_dao, outbox_dao):
    return DeckTaskService(sessionmaker, deckitem_dao, decktask_dao, outbox_dao)


@pytest_asyncio.fixture
async def scheduler(decktask_service, sessionmaker, outbox_dao):
    return RetryScheduler(decktask_service, sessionmaker, outbox_dao)


@pytest_asyncio.fixture
async def fake_normalizer():
    return FakeNormalizer()


@pytest_asyncio.fixture
async def fake_context_generator():
    return FakeContextGenerator()


@pytest_asyncio.fixture
async def fake_anki():
    return FakeAnki()


@pytest_asyncio.fixture
async def pipeline(
    decktask_service,
    deckitem_service,
    deckcard_service,
    fake_normalizer,
    fake_context_generator,
    fake_anki,
):
    return DeckPipeline(
        decktask_service,
        deckitem_service,
        deckcard_service,
        fake_normalizer,
        fake_context_generator,
        fake_anki,
    )


# worker fixtures


class FakePipeline(DeckPipeline):
    def __init__(self):
        self.attempted_task_ids: list[UUID] = []
        self.processed_task_ids: list[UUID] = []
        self.fail_for_task_ids = set()
        self.event: asyncio.Event = asyncio.Event()

    async def run(self, task_id: UUID):
        self.attempted_task_ids.append(task_id)
        if task_id in self.fail_for_task_ids:
            raise RuntimeError("pipeline failed")

        self.processed_task_ids.append(task_id)
        self.event.set()


class TestPipelineProvider(Provider):
    def __init__(self, pipeline: DeckPipeline):
        super().__init__()
        self._pipeline = pipeline

    @provide(scope=Scope.REQUEST)
    def get_pipeline(self) -> DeckPipeline:
        return self._pipeline


class FakeDeckTaskService(DeckTaskService):
    def __init__(self):
        self.retried: list[tuple[UUID, Exception]] = []

    async def mark_for_retry_or_fail(self, task_id: UUID, error: Exception):
        self.retried.append((task_id, error))


class TestTaskServiceProvider(Provider):
    def __init__(self, service: FakeDeckTaskService):
        super().__init__()
        self._service = service

    @provide(scope=Scope.REQUEST)
    async def get_task_service(self) -> DeckTaskService:
        return self._service


@pytest_asyncio.fixture
async def rabbit_config():
    return Config(
        rabbitmq=RabbitMQConfig(
            url="amqp://rmuser:rmpassword@localhost:5673/",
            queue_name=f"pipeline_queue_test_{uuid.uuid4().hex}",
        )
    )


@pytest_asyncio.fixture
async def fake_pipeline():
    return FakePipeline()


@pytest_asyncio.fixture
async def fake_task_service():
    return FakeDeckTaskService()


@pytest_asyncio.fixture
async def broker(rabbit_config):
    return RabbitBroker(rabbit_config.rabbitmq.url)


@pytest_asyncio.fixture
async def publisher(rabbit_config, broker):
    return RabbitPublisher(broker=broker, queue_name=rabbit_config.queue_name)


@pytest_asyncio.fixture
async def faststream_app(rabbit_config, fake_pipeline, fake_task_service, broker):
    router = setup_worker(queue_name=rabbit_config.rabbitmq.queue_name)
    broker.include_router(router)

    container = make_async_container(
        TestPipelineProvider(fake_pipeline),
        TestTaskServiceProvider(fake_task_service),
    )

    faststream_app = FastStream(broker)
    setup_dishka_faststream(container, faststream_app)

    await faststream_app.start()
    yield faststream_app
    await faststream_app.stop()
