from typing import List, Optional
from uuid import UUID

from django.db import IntegrityError
from api.assign.models.Assign import Assign
from api.truck.models.Truck import Truck
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.assign.models.Assign import AssignAudit

class RepositoryAssign():

    def create_assign(self, operator_id: int, truck_id: Optional[int], order_id: UUID, additional_costs: float, rol: Optional[str] = None) -> Assign:
        """Crea una nueva asignación entre un operador, un camión y un pedido."""
        operator = Operator.objects.get(id_operator=operator_id)
        truck = Truck.objects.get(id_truck=truck_id) if truck_id else None
        order = Order.objects.get(key=order_id)
        return Assign.objects.create(
            operator=operator,
            truck=truck,
            order=order,
            additional_costs=additional_costs,
            rol=rol
        )
    @staticmethod
    def create_bulk(assignments):
        try:
            Assign.objects.bulk_create(assignments)
            return True, None
        except IntegrityError:
            return False, "Asignación duplicada o violación de restricciones"
        except Exception as e:
            return False, str(e)

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

    def update_assign(self, assign_id: int, assign_data: dict) -> Optional[Assign]:
        """Actualiza una asignación"""
        try:
            assign = Assign.objects.get(id=assign_id)
            
            original_values = {}
            for key in assign_data.keys():
                if hasattr(assign, key):
                    original_values[key] = getattr(assign, key)
                    
            for key, value in assign_data.items():
                if hasattr(assign, key):
                    setattr(assign, key, value)
            
            assign.save()
            return assign
            
        except Assign.DoesNotExist:
            return None
        except IntegrityError as e:
            raise IntegrityError(e)
            
    def get_assign_audit_history(self, assign_id: int) -> List[dict]:
        """Recupera el historial de auditoría de una asignación"""
        try:
            assign = Assign.objects.get(id=assign_id)
            audit_records = AssignAudit.objects.filter(assign=assign).order_by('-modified_at')
            result = []
            for record in audit_records:
                result.append({
                    'id': record.id,
                    'old_operator': record.old_operator.id_operator if record.old_operator else None,
                    'new_operator': record.new_operator.id_operator if record.new_operator else None,
                    'old_order': record.old_order.key if record.old_order else None,
                    'new_order': record.new_order.key if record.new_order else None,
                    'old_truck': record.old_truck.id_truck if record.old_truck else None,
                    'new_truck': record.new_truck.id_truck if record.new_truck else None,
                    'old_payment': record.old_payment.id if record.old_payment else None,
                    'new_payment': record.new_payment.id if record.new_payment else None,
                    'old_assigned_at': record.old_assigned_at,
                    'new_assigned_at': record.new_assigned_at,
                    'old_rol': record.old_rol,
                    'new_rol': record.new_rol,
                    'modified_at': record.modified_at
                })
            return result
        except Assign.DoesNotExist:
            return []

    def verify_assign_integrity(self):
        existing_assign = Assign.objects.filter(
            operator__id_operator=1001,  # Cambia esto por el ID real
            order__key="1234567890ABCDEF1234567890ABCDEF",  # Cambia esto por la clave real
            truck__id_truck=1,  # Cambia esto por el ID real
            id_pay=2  # Asegúrate de que este ID exista
        ).first()
        return existing_assign is not None
