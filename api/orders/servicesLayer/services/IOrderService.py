from abc import ABC, abstractmethod
from typing import Dict
from api.orders.servicesLayer.dtos.PostOrderDTO import PostOrderDTO 

class IOrderService(ABC):
    """ Interface for defining order service operations """

    @abstractmethod
    def create_order(self, order_data: Dict) -> PostOrderDTO:
        """ Creates a new order and returns a DTO """
        pass
