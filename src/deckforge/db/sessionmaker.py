from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from deckforge.config import PostgresConfig


async def new_sessionmaker(
    psql_config: PostgresConfig,
) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(url=psql_config.url)
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
