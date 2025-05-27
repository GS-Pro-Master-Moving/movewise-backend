class IServicesOrder:
    def create_order(self, data):
        pass
    def update_order(self, order, data):
        pass
    def update_status(self, url, order):
        """
        Updates the status of an order recieving a evidence URL.
        """
        pass
    def get_all_pending_orders(self):
        """
        Retrieves all orders.
        """
        pass
    def delete_order_with_status(self, order_key):
        """
        Deletes an order if its status is "Finished".

        Args:
        - order_key: The key of the order to be deleted.

        Returns:
        - A message indicating the result of the operation.
        """
        pass