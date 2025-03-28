from typing import List, Optional
from uuid import UUID  # Importar UUID
from django.db import transaction
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.assign.models.Assign import Assign
from api.assign.repositories.RepositoryAssign import RepositoryAssign
from api.assign.services.IServicesAssign import IServicesAssign

class ServicesAssign(IServicesAssign):
    def __init__(self):
        self.repository = RepositoryAssign()

    def create_assign(self, operator_id: int, truck_id: int, order_id: UUID) -> Assign:
        """Creates a new assignment between an operator, a truck, and an order."""
        return self.repository.create_assign(operator_id, truck_id, order_id)
    
    @staticmethod
    def create_assignments(self, data):
        """Procesa los datos y crea asignaciones en la base de datos"""
        assignments = []

        try:
            with transaction.atomic():  # Si algo falla, revierte todo
                for item in data:
                    operator = Operator.objects.get(id_operator=item["id_operator"])
                    order = Order.objects.get(key=item["key"])
                    truck = Truck.objects.get(id_truck=item["id_truck"]) if "id_truck" in item else None

                    assignments.append(Assign(operator=operator, order=order, truck=truck, rol=item.get("rol")))
                success, error = self.repository.create_bulk(assignments)

                if not success:
                    return False, error

            return True, "Assignments created successfully"

        except Operator.DoesNotExist:
            return False, "One or more operators not found"
        except Order.DoesNotExist:
            return False, "One or more orders not found"
        except Truck.DoesNotExist:
            return False, "One or more trucks not found"
        except Exception as e:
            return False, str(e)

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
