from abc import ABC, abstractmethod
from typing import List

from api.assign.models.Assign import Assign

class IRepositoryOperator(ABC):
    @abstractmethod
    def create(self, data):
        pass
    
    @abstractmethod
    def get_all_assigns(self) -> List[Assign]:
        pass
    
    @abstractmethod
    def get_all(self):
        pass
    
    @abstractmethod
    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        pass

    @abstractmethod
    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        pass