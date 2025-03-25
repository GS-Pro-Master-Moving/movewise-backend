from typing import List, Optional
from uuid import UUID  # Importar UUID
from api.assign.models.Assign import Assign
from api.assign.repositories.RepositoryAssign import RepositoryAssign
from api.assign.services.IServicesAssign import IServicesAssign

class ServicesAssign(IServicesAssign):
    def __init__(self):
        self.repository = RepositoryAssign()

    def create_assign(self, operator_id: int, truck_id: int, order_id: UUID) -> Assign:
        """Creates a new assignment between an operator, a truck, and an order."""
        return self.repository.create_assign(operator_id, truck_id, order_id)

    def get_assign_by_id(self, assign_id: int) -> Optional[Assign]:
        """Retrieves an assignment by ID"""
        return self.repository.get_assign_by_id(assign_id)

    def get_assigns_by_operator(self, operator_id: int) -> List[Assign]:
        """Retrieves all assignments for a specific operator"""
        return self.repository.get_assigns_by_operator(operator_id)

    def get_assigns_by_order(self, order_id: UUID) -> List[Assign]:  
        """Retrieves all assignments for a specific order"""
        return self.repository.get_assigns_by_order(order_id)

    def update_assign_status(self, assign_id: int, new_status: str) -> Assign:
        """Updates the status of an assignment"""
        return self.repository.update_assign_status(assign_id, new_status)

    def delete_assign(self, assign_id: int) -> None:
        """Deletes an assignment"""
        self.repository.delete_assign(assign_id)
