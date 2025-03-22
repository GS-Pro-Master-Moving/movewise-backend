from order.repositories.RepositoryOrder import RepositoryOrder
from order.services.IServicesOrder import IServicesOrder
class ServicesOrder(IServicesOrder):
    def __init__(self):
        self.repository = RepositoryOrder()

    def create_order(self, data):
        return self.repository.create_order(data)
