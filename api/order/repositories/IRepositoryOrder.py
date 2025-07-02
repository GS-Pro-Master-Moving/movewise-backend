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

    def filter_by_location(self, company_id, country=None, state=None, city=None):
        """
        Filter orders by location (country, state, city).
        
        Args:
        - company_id: ID of the company
        - country: Optional country filter
        - state: Optional state filter
        - city: Optional city filter
        
        Returns:
        - QuerySet of filtered orders
        """
        raise NotImplementedError