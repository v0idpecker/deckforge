from dishka import make_async_container
from dishka.async_container import AsyncContainer
from faststream.rabbit.broker import RabbitBroker

from deckforge.config import Config
from deckforge.di.providers import (
    AMQPProvider,
    DAOProvider,
    DBProvider,
    PipelineProvider,
    ServiceProvider,
)


def setup_container(config: Config, broker: RabbitBroker) -> AsyncContainer:
    container = make_async_container(
        DBProvider(),
        DAOProvider(),
        ServiceProvider(),
        AMQPProvider(),
        PipelineProvider(),
        context={
            Config: config,
            RabbitBroker: broker,
        },
    )
    return container
