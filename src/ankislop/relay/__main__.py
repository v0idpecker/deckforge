import asyncio

from dotenv import load_dotenv

from ankislop.adapters.amqp.broker import new_broker
from ankislop.adapters.amqp.queue_publisher import RabbitPublisher
from ankislop.config import create_config
from ankislop.db.dao.outbox import OutboxEventDAO
from ankislop.db.sessionmaker import new_sessionmaker
from ankislop.logging_setup import setup_logging
from ankislop.relay.service import OutboxRelay

load_dotenv()

async def main():
    config = create_config()
    setup_logging(config.logging.level, config.logging.format)

    broker = new_broker(config.rabbitmq)
    publisher = RabbitPublisher(broker=broker, queue_name=config.rabbitmq.queue_name)
    sessionmaker = await new_sessionmaker(config.postgres)
    dao = OutboxEventDAO()
    relay = OutboxRelay(sessionmaker, dao, publisher)

    await broker.start()
    try:
        await relay.run_polling_loop()
    finally:
        await broker.stop()

if __name__ == "__main__":
    asyncio.run(main())
