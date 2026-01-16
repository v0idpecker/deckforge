from dishka import make_async_container
from dishka.async_container import AsyncContainer

from deckforge.config import Config
from deckforge.di.providers import DBProvider


def setup_container(config: Config) -> AsyncContainer:
    container = make_async_container(DBProvider(), context={Config: config})
    return container
