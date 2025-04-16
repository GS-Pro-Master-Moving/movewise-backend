from typing import List, Optional, Dict
from api.costFuel.models.CostFuel import CostFuel

class IRepositoryCostFuel:
    """Interface for CostFuel repository operations."""
    
    def get_all(self) -> List[CostFuel]:
        """Returns all cost fuel records."""
        pass
    
    def get_by_id(self, id_fuel: int) -> Optional[CostFuel]:
        """Returns a cost fuel record by its ID."""
        pass
    
    def get_by_order(self, order_key) -> List[CostFuel]:
        """Returns cost fuel records associated with an order."""
        pass
    
    def get_by_truck(self, truck_id: int) -> List[CostFuel]:
        """Returns cost fuel records associated with a truck."""
        pass
    
    def create_cost_fuel(self, cost_fuel_data: Dict) -> CostFuel:
        """Creates a new cost fuel record."""
        pass
    
    def update_cost_fuel(self, id_fuel: int, cost_fuel_data: Dict) -> Optional[CostFuel]:
        """Updates an existing cost fuel record."""
        pass
    
    def delete_cost_fuel(self, id_fuel: int) -> bool:
        """Deletes a cost fuel record."""
        pass