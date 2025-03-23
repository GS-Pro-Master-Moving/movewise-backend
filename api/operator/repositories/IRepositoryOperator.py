from abc import ABC, abstractmethod

class IRepositoryOperator(ABC):
    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        pass

    @abstractmethod
    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        pass