from abc import ABC, abstractmethod

class IRepositoryOperator(ABC):
    @abstractmethod
    def create(self, data):
        pass
