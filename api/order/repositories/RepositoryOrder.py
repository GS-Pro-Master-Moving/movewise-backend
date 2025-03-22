from order.repositories.RepositoryOrder import IRepositoryOrder

class RepositoryOrder(IRepositoryOrder):
    @staticmethod
    def create_order(data):
        return super().create_order(data)
