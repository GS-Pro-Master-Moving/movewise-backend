from typing import List, Optional
from uuid import UUID  # Importar UUID
from django.db import transaction, IntegrityError
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.assign.models.Assign import Assign
from api.assign.repositories.RepositoryAssign import RepositoryAssign
from django.utils import timezone
from django.db import models

class ServicesAssign:
    def __init__(self):
        self.repository = RepositoryAssign()

    # ServicesAssign.py
    def create_assign(self, operator_id: int, truck_id: Optional[int], order_id: str, additional_costs: float) -> Assign:
        """Creates a new assignment between an operator, a truck, and an order."""
        # Validaciones de negocio
        if not operator_id or not order_id:
            raise ValueError("Operator ID and Order ID must be provided")
        
        # Convertir order_id a UUID si es necesario
        try:
            order_uuid = UUID(order_id)
        except ValueError:
            raise ValueError("Invalid Order ID format")

        return self.repository.create_assign(
            operator_id=operator_id,
            truck_id=truck_id,
            order_id=order_uuid,
            additional_costs=additional_costs
    )
    
    @staticmethod
    def create_assignments(data):
        """Procesa los datos y crea asignaciones en la base de datos"""
        assignments = []

        try:
            with transaction.atomic():  # Si algo falla, revierte todo
                for item in data:
                    operator = Operator.objects.get(id_operator=item["id_operator"])
                    order = Order.objects.get(key=item["key"])
                    truck = Truck.objects.get(id_truck=item["id_truck"]) if "id_truck" in item else None

                    # Validaciones adicionales
                    if not operator or not order:
                        raise ValueError("Invalid operator or order in the provided data")

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
        
    #to audit table assign
    def get_assign(self, assign_id: int) -> Optional[Assign]:
        """Retrieves an assignment by ID"""
        return self.repository.get_assign_by_id(assign_id)

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
        # Validación del estado
        if new_status not in ["pending", "completed", "canceled"]:
            raise ValueError("Invalid status provided")

        return self.repository.update_assign_status(assign_id, new_status)

    def delete_assign(self, assign_id: int) -> None:
        """Deletes an assignment"""
        existing_assign = self.repository.get_assign_by_id(assign_id)
        if not existing_assign:
            raise ValueError("Assignment not found")

        self.repository.delete_assign(assign_id)

    def get_assign_audit_history(self, assign_id: int) -> List[dict]:
        """Retrieves the audit history of an assignment"""
        return self.repository.get_assign_audit_history(assign_id)
        
    def update_assign(self, assign_id: int, assign_data: dict) -> Optional[Assign]:
        """Updates an assignment with the provided data"""
        try:
            # Get the existing assignment
            assign = self.repository.get_assign_by_id(assign_id)
            if not assign:
                return None
                
            # Update the assignment - dejamos que el repositorio maneje la actualización
            # y la creación del registro de auditoría a través del método save() del modelo
            return self.repository.update_assign(assign_id, assign_data)
        except IntegrityError as e:
            # Podemos manejar específicamente errores de integridad aquí
            # por ejemplo, registrar el error o notificar
            raise e
        except Exception as e:
            # Otras excepciones
            return None

