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
    def get_all_orders():
        pass
    """
        Deletes an order if its status is "Finished".

        Args:
        - order_key: The key of the order to be deleted.

        Returns:
        - A message indicating the result of the operation.
        """
    def delete_order_with_status(self, order_key):
        pass