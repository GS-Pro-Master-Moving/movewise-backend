
from abc import ABC, abstractmethod


class IRepositoryCompany(ABC):
    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id: int):
        pass
    
    def get_by_name(self, name: str):
        pass

    @abstractmethod
    def create(self, company):
        pass

    @abstractmethod
    def update(self, company):
        pass

    @abstractmethod
    def delete(self, id: int):
        pass