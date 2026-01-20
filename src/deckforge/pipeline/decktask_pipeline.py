from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService


class DeckTaskPipeline:
    def __init__(
        self, decktask_service: DeckTaskService, deckitem_service: DeckItemSerivce
    ):
        self.decktask_service = decktask_service
        self.deckitem_service = deckitem_service
