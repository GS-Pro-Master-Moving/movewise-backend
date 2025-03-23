from abc import ABC, abstractmethod

class IServiceOperator(ABC):
    @abstractmethod
    def create_operator(self, data):
        pass
