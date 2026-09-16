from abc import abstractmethod
from typing import Protocol


class DAO(Protocol):
    @abstractmethod
    async def list(self, session):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data, session):
        raise NotImplementedError
