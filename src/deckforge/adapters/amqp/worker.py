from uuid import UUID

from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit.broker.router import RabbitRouter

from deckforge.pipeline.deck_pipeline import DeckPipeline

AMQPRouter = RabbitRouter()


def setup_worker(queue_name: str) -> RabbitRouter:
    @AMQPRouter.subscriber(queue_name)
    @inject
    async def handle(task_id: str, *, pipeline: FromDishka[DeckPipeline]):
        await pipeline.run(UUID(task_id))

    return AMQPRouter
