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
        
    def generate_freelance_code(self, company_id: int) -> str:
        """
        Genera un código único para un freelancer en el formato FRL-0001, FRL-0002, etc.
        """
        # Obtener el último código de freelancer para esta compañía
        last_freelance = Operator.objects.filter(
            person__id_company=company_id,
            code__startswith='FRL-'
        ).order_by('-code').first()
        
        if not last_freelance or not last_freelance.code:
            return "FRL-0001"
            
        try:
            # Extraer el número del último código y sumar 1
            last_number = int(last_freelance.code.split('-')[1])
            next_number = last_number + 1
            return f"FRL-{next_number:04d}"
        except (IndexError, ValueError):
            # En caso de error en el formato, empezar desde 1
            return "FRL-0001"
            
    def create_freelance_operator(self, validated_data, person_data, company_id):
        """
        Crea un nuevo operador freelance con código generado automáticamente
        """
        from django.db import transaction
        from api.person.models.Person import Person
        from api.operator.models.Operator import Operator
        
        with transaction.atomic():
            # Crear la persona primero
            person = Person.objects.create(**person_data, id_company_id=company_id)
            
            # Generar código único para el freelancer
            code = self.generate_freelance_code(company_id)
            
            # Crear el operador con status='freelance' y el código generado
            operator_data = {
                **validated_data,
                'person': person,
                'code': code,
                'status': 'freelance'
            }
            
            operator = Operator.objects.create(**operator_data)
            return operator