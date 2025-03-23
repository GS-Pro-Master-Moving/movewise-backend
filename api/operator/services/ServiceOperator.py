from api.operator.repositories import OperatorRepository
from api.operator.services.IServicesOperator import IServiceOperator  

class OperatorService(IServiceOperator):
    def __init__(self, repository=None):
        self.repository = repository or OperatorRepository()

    def create_operator(self, data):
        return self.repository.create(data)
