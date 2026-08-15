import asyncio

from dishka import AsyncContainer, make_async_container
from dotenv import load_dotenv

from deckforge.config import Config, create_config
from deckforge.di.providers import (
    DAOProvider,
    DBProvider,
    ServiceProvider,
    WordProcessingProvider,
)
from deckforge.scheduler.service import RetryScheduler, SchedulerProvider

load_dotenv()


async def run_retry_scheduler(container: AsyncContainer, interval=15):
    while True:
        try:
            async with container() as request_container:
                scheduler = await request_container.get(RetryScheduler)
                await scheduler.tick()
                await asyncio.sleep(interval)
        except Exception:
            await asyncio.sleep(interval)


async def main():
    config = create_config()
    container = make_async_container(
        DBProvider(),
        DAOProvider(),
        ServiceProvider(),
        SchedulerProvider(),
        WordProcessingProvider(),
        context={Config: config},
    )

    print("Scheduler is running!")
    await run_retry_scheduler(container)


if __name__ == "__main__":
    asyncio.run(main())
