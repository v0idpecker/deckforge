from faststream.rabbit import RabbitBroker

from ankislop.config import RabbitMQConfig


def new_broker(rabbit_config: RabbitMQConfig) -> RabbitBroker:
    return RabbitBroker(rabbit_config.url)
