from abc import ABC, abstractmethod
from typing import List, Optional
from api.assign.models.Assign import Assign

class IRepositoryAssign(ABC):

    @abstractmethod
    def create_assign(self, operator_id: int, order_id: int) -> Assign:
        """Creates a new assignment between an operator and an order"""
        pass

    @abstractmethod
    def get_assign_by_id(self, assign_id: int) -> Optional[Assign]:
        """Retrieves an assignment by ID"""
        pass

    @abstractmethod
    def get_assigns_by_operator(self, operator_id: int) -> List[Assign]:
        """Retrieves all assignments for a specific operator"""
        pass

    @abstractmethod
    def get_assigns_by_order(self, order_id: int) -> List[Assign]:
        """Retrieves all assignments for a specific order"""
        pass

    @abstractmethod
    def update_assign_status(self, assign_id: int, new_status: str) -> Assign:
        """Updates the status of an assignment"""
        pass

    @abstractmethod
    def delete_assign(self, assign_id: int) -> None:
        """Deletes an assignment"""
        pass
