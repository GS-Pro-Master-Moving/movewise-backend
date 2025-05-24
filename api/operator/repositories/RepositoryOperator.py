from typing import List
from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.operator.repositories.IRepositoryOperator import IRepositoryOperator

class RepositoryOperator(IRepositoryOperator):
    def create(self, data):
        return Operator.objects.create(**data)
    
    def get_all_assigns(self):
        return Assign.objects.all()
    
    def get_all(self, company_id) -> List[Operator]:
        # Filtrar solo operadores activos de la compañía especificada
        return Operator.objects.active().filter(person__id_company=company_id)
    
    def get_freelance_operators(self, company_id):
        return Operator.objects.select_related('person')\
            .filter(
                person__id_company=company_id,
                status__in=['freelance', 'active']
            )\
            .order_by('-id_operator')
    
    def get_freelance_by_code(self, company_id, code):
        return Operator.objects.select_related('person')\
            .filter(
                person__id_company=company_id,
                code=code,
                status__in=['freelance', 'active']
            )\
            .first()

    
    def get_by_id(self, operator_id: int):
    # Obtener un operador cuyo estado NO sea 'inactive'
        try:
            return Operator.objects.exclude(status='inactive').get(id_operator=operator_id)
        except Operator.DoesNotExist:
            return None
    
    def get_by_number_id(self, document_number: str):
        # Obtener un operador activo por número de documento
        try:
            return Operator.objects.active().get(person__id_number=document_number)
        except Operator.DoesNotExist:
            return None
    def get_by_code(self, code: str):
        try:
            return Operator.objects.active().get(code=code)
        except Operator.DoesNotExist:
            return None

    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        # Actualizar solo operadores activos
        Operator.objects.active().filter(id_operator=operator_id).update(name_t_shift=new_name_t_shift)

    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        # Actualizar solo operadores activos
        Operator.objects.active().filter(id_operator=operator_id).update(size_t_shift=new_size_t_shift)
    
    def soft_delete(self, operator_id: int):
        # Realizar soft delete cambiando status a 'inactive'
        try:
            operator = Operator.objects.get(id_operator=operator_id)
            operator.soft_delete()
            return True
        except Operator.DoesNotExist:
            return False