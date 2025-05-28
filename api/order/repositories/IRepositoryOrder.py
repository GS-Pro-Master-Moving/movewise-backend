from api.order.models.Order import Order

class IRepositoryOrder:
    """
    Interface for Order Repository.
    """
    """
    Create a new order.
    """
    def create_order(data):
        pass
    """
    Update an existing order.
    """
    def update_order(order, data):
        pass
    """
    Update the status of an order.
    """
    def update_status(url, order):
        pass
    """
    Get all orders.
    """
    def get_all_pending_orders(self, company_id):
        """
        Return all orders belonging to company_id.
        """
        raise NotImplementedError
