from dishka.integrations.faststream import FromDishka
from faststream.rabbit.broker.router import RabbitRouter

from deckforge.pipeline.deck_pipeline import DeckPipeline

AMQPRouter = RabbitRouter()


def setup_worker(queue_name: str) -> RabbitRouter:
    @AMQPRouter.subscriber(queue_name)
    async def handle(task_id: str, pipeline: FromDishka[DeckPipeline]):
        await pipeline.run(task_id)

    return AMQPRouter
