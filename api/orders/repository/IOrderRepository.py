from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

T = TypeVar("T")  #Generic type for models

class IOrderRepository(ABC, Generic[T]):
    """ Abstract repository interface for CRUD operations """

    @abstractmethod
    def create(self, data: dict) -> T:
        """ Creates and saves a new instance in the database """
        pass
