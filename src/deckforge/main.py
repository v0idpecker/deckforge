import os
from contextlib import asynccontextmanager
from pathlib import Path

from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream import FastStream
from starlette.middleware.sessions import SessionMiddleware

from deckforge.adapters.amqp.broker import new_broker
from deckforge.adapters.amqp.worker import setup_worker
from deckforge.api.handlers import router
from deckforge.config import create_config
from deckforge.di.setup_container import setup_container

load_dotenv()

media_dir_path = Path("media")

if not media_dir_path.is_dir():
    os.mkdir("media")

config = create_config()

print(config.app.backend_public_url)

broker = new_broker(config.rabbitmq)
amqp_router = setup_worker(config.rabbitmq.queue_name)
faststream_app = FastStream(broker)
container = setup_container(config=config, broker=broker)
setup_dishka_faststream(container, faststream_app, auto_inject=True)
broker.include_router(amqp_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await faststream_app.start()
    yield
    await faststream_app.stop()


def get_fastapi_app() -> FastAPI:
    app = FastAPI(title="Deck Forge", lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.security.session_secret,
        same_site="lax",
        https_only=False,
    )

    setup_dishka_fastapi(app=app, container=container)
    return app


app = get_fastapi_app()
