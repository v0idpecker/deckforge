import logging
from uuid import UUID

from dishka.integrations.faststream import FromDishka, inject
from faststream import Context
from faststream.rabbit.broker.router import RabbitRouter

from deckforge.logging_setup import set_task_id
from deckforge.pipeline.deck_pipeline import DeckPipeline
from deckforge.services.decks.decktask import DeckTaskService

logger = logging.getLogger(__name__)

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
        set_task_id(task_id)
        logger.info("Received task from queue")

        try:
            await pipeline.run(UUID(task_id))
        except Exception as e:
            logger.exception("Pipeline failed for task %s", task_id)

            try:
                await service.mark_for_retry_or_fail(UUID(task_id), e)
                await message.ack()
                logger.info("Task %s scheduled for retry and acknowledged", task_id)
            except Exception:
                logger.exception(
                    "Failed to mark task %s for retry, requeueing message", task_id
                )
                await message.nack(requeue=True)
        else:
            logger.info("Task %s processed successfully", task_id)

    return AMQPRouter
