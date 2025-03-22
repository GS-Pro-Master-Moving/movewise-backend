from api.order.repositories.IRepositoryOrder import IRepositoryOrder
from api.order.models.Order import Order
class RepositoryOrder(IRepositoryOrder):
    @staticmethod
    def create_order(data):
        return Order.objects.create(**data)
