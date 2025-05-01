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
        return Operator.objects.filter(person__id_company=company_id)
    
    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        Operator.objects.filter(id_operator=operator_id).update(name_t_shift=new_name_t_shift)

    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        Operator.objects.filter(id_operator=operator_id).update(size_t_shift=new_size_t_shift)