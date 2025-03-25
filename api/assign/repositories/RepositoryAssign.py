from typing import List, Optional
from uuid import UUID  # Importar UUID
from api.assign.models.Assign import Assign
from api.assign.repositories.IRepositoryAssign import IRepositoryAssign
from api.truck.models.Truck import Truck
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
class RepositoryAssign(IRepositoryAssign):

    def create_assign(self, operator_id: int, truck_id: int, order_id: UUID) -> Assign:
        """Creates a new assignment between an operator, a truck, and an order."""
        operator = Operator.objects.get(id_operator=operator_id)
        truck = Truck.objects.get(id_truck=truck_id)
        order = Order.objects.get(key=order_id)
        # Creates a new assignment with the keys of the operator, truck, and order
        return Assign.objects.create(operator=operator, truck=truck, order=order)

    def get_assign_by_id(self, assign_id: int) -> Optional[Assign]:
        try:
            return Assign.objects.get(id=assign_id)
        except Assign.DoesNotExist:
            return None

    def get_assigns_by_operator(self, operator_id: int) -> List[Assign]:
        return list(Assign.objects.filter(operator_id=operator_id))

    def get_assigns_by_order(self, order_id: UUID) -> List[Assign]:  
        return list(Assign.objects.filter(order_id=order_id))

    def update_assign_status(self, assign_id: int, new_status: str) -> Optional[Assign]:
        assign = self.get_assign_by_id(assign_id)
        if assign:
            assign.status = new_status
            assign.save()
        return assign

    def delete_assign(self, assign_id: int) -> None:
        assign = self.get_assign_by_id(assign_id)
        if assign:
            assign.delete()
