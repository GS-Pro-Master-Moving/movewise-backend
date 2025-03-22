from order.models import Order

class IRepositoryOrder:
    @staticmethod
    def create_order(data):
        return Order.objects.create(**data)
