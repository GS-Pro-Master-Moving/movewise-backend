from typing import List
from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.operator.repositories.RepositoryOperator import RepositoryOperator
from api.operator.services.IServicesOperator import IServiceOperator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck  
from api.person.models import Person

class ServiceOperator(IServiceOperator):
    def __init__(self, repository=None):
        self.repository = repository or RepositoryOperator()
        
    def create_operator(self, validated_data):
        pass  

    # service.py
    def get_all_operators(self, company_id) -> List[Operator]:
        return self.repository.get_all(company_id)

    def get_freelance_operators(self, company_id):
        if not company_id:
            raise ValueError("Company context missing")
        
        return self.repository.get_freelance_operators(company_id)
    
    def get_freelance_operator_by_code(self, company_id: int, code: str):
        if not company_id:
            raise ValueError("Se requiere el contexto de la compañía")
        if not code:
            raise ValueError("El código del operador es requerido")
            
        return self.repository.get_freelance_by_code(company_id, code)
    
    def get_operator_by_id(self, operator_id: int):
        return self.repository.get_by_id(operator_id)
    
    def get_operator_by_number_id(self, document_number: str):
        return self.repository.get_by_number_id(document_number)
    
    def get_operator_by_code(self, code: str):
        print(f'codigo en el servicio: {code}')
        return self.repository.get_by_code(code)
    
    def get_all_assigns(self):
        return self.repository.get_all_assigns()
    
    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        self.repository.update_name_t_shift(operator_id, new_name_t_shift)

    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        self.repository.update_size_t_shift(operator_id, new_size_t_shift)
    
    def delete_operator(self, operator_id: int):
        """
        Realiza un soft delete del operador cambiando su estado a 'inactive'
        """
        return self.repository.soft_delete(operator_id)