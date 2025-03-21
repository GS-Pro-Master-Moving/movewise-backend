from api.orders.model.Order import Order
from api.orders.repository.IOrderRepository import IOrderRepository
from typing import Optional

class OrderRepository(IOrderRepository[Order]):
    """ Repository for handling database operations related to orders """

    def create(self, order_data: dict) -> Order:
        return Order.objects.create(**order_data)
