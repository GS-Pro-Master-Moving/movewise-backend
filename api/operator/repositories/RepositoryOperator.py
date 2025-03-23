from api.operator.models.Operator import Operator
from api.operator.repositories import IRepositoryOperator

class OperatorRepository(IRepositoryOperator):
    def create(self, data):
        return Operator.objects.create(**data)
