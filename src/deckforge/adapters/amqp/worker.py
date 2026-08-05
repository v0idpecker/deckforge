from uuid import UUID

from dishka.integrations.faststream import FromDishka, inject
from faststream import Context
from faststream.rabbit.broker.router import RabbitRouter

from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.services.decks.decktask import DeckTaskService

AMQPRouter = RabbitRouter()


def setup_worker(queue_name: str) -> RabbitRouter:
    @AMQPRouter.subscriber(queue_name)
    @inject
    async def handle(
        task_id: str,
        *,
        pipeline: FromDishka[DeckPipeline],
        service: FromDishka[DeckTaskService],
        message=Context("message"),
    ):
        try:
            await pipeline.run(UUID(task_id))
        except Exception as e:
            try:
                await service.mark_for_retry_or_fail(UUID(task_id), e)
                await message.ack()
            except Exception:
                await message.nack(requeue=True)

    return AMQPRouter
