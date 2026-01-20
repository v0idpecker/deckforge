from pydantic import BaseModel


class DeckTaskCreateRequest(BaseModel):
    words: list[str]
    options: dict
