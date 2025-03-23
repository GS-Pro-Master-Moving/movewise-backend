from typing import List, Optional
from api.assign.models.Assign import Assign
from api.assign.repositories.IRepositoryAssign import IRepositoryAssign

class RepositoryAssign(IRepositoryAssign):

    def create_assign(self, operator_id: int, order_id: int) -> Assign:
        assign, created = Assign.objects.get_or_create(operator_id=operator_id, order_id=order_id)
        return assign

    def get_assign_by_id(self, assign_id: int) -> Optional[Assign]:
        try:
            return Assign.objects.get(id=assign_id)
        except Assign.DoesNotExist:
            return None

    def get_assigns_by_operator(self, operator_id: int) -> List[Assign]:
        return Assign.objects.filter(operator_id=operator_id)

    def get_assigns_by_order(self, order_id: int) -> List[Assign]:
        return Assign.objects.filter(order_id=order_id)

    def update_assign_status(self, assign_id: int, new_status: str) -> Assign:
        assign = self.get_assign_by_id(assign_id)
        if assign:
            assign.status = new_status
            assign.save()
        return assign

    def delete_assign(self, assign_id: int) -> None:
        assign = self.get_assign_by_id(assign_id)
        if assign:
            assign.delete()
