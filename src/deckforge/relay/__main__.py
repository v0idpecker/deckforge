import asyncio

from dotenv import load_dotenv

from deckforge.adapters.amqp.broker import new_broker
from deckforge.adapters.amqp.queue_publisher import RabbitPublisher
from deckforge.config import create_config
from deckforge.db.dao.outbox import OutboxEventDAO
from deckforge.db.sessionmaker import new_sessionmaker
from deckforge.relay.service import OutboxRelay

load_dotenv()


async def main():
    config = create_config()
    broker = new_broker(config.rabbitmq)
    publisher = RabbitPublisher(broker=broker, queue_name=config.rabbitmq.queue_name)
    sessionmaker = await new_sessionmaker(config.postgres)
    dao = OutboxEventDAO()
    relay = OutboxRelay(sessionmaker, dao, publisher)

    print(config.rabbitmq.url)
    print("Запуск!")
    await broker.start()
    try:
        await relay.run_polling_loop()
    finally:
        await broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
