from typing import List, Optional, Dict
from api.costFuel.models.CostFuel import CostFuel
from api.costFuel.repositories.RepositoryCostFuel import RepositoryCostFuel
from api.costFuel.services.IServicesCostFuel import IServicesCostFuel

class ServicesCostFuel(IServicesCostFuel):
    """Implementation of the CostFuel service interface."""
    
    def __init__(self):
        self.repository = RepositoryCostFuel()
    
    def get_all(self) -> List[CostFuel]:
        """Returns all cost fuel records."""
        return self.repository.get_all()
    
    def get_by_id(self, id_fuel: int) -> Optional[CostFuel]:
        """Returns a cost fuel record by its ID."""
        return self.repository.get_by_id(id_fuel)
    
    def get_by_order(self, order_key) -> List[CostFuel]:
        """Returns cost fuel records associated with an order."""
        return self.repository.get_by_order(order_key)
    
    def get_by_truck(self, truck_id: int) -> List[CostFuel]:
        """Returns cost fuel records associated with a truck."""
        return self.repository.get_by_truck(truck_id)
    
    def create_cost_fuel(self, cost_fuel_data: Dict) -> CostFuel:
        """Creates a new cost fuel record."""
        return self.repository.create_cost_fuel(cost_fuel_data)
    
    def update_cost_fuel(self, id_fuel: int, cost_fuel_data: Dict) -> Optional[CostFuel]:
        """Updates an existing cost fuel record."""
        return self.repository.update_cost_fuel(id_fuel, cost_fuel_data)
    
    def delete_cost_fuel(self, id_fuel: int) -> bool:
        """Deletes a cost fuel record."""
        return self.repository.delete_cost_fuel(id_fuel)