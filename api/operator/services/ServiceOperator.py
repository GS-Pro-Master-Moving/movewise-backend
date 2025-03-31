from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.operator.repositories.RepositoryOperator import RepositoryOperator
from api.operator.services.IServicesOperator import IServiceOperator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck  

class ServiceOperator(IServiceOperator):
    def __init__(self, repository=None):
        self.repository = repository or RepositoryOperator()
        
    def create_operator(self, data):
        return self.repository.create(data)
    def get_all_operators(self):
        return self.repository.get_all()
    
    def get_all_assigns(self):
        return self.repository.get_all_assigns()
    
    def update_name_t_shift(self, operator_id: int, new_name_t_shift: str):
        self.repository.update_name_t_shift(operator_id, new_name_t_shift)

    def update_size_t_shift(self, operator_id: int, new_size_t_shift: str):
        self.repository.update_size_t_shift(operator_id, new_size_t_shift)