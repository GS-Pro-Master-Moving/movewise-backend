from typing import List, Optional, Dict
from api.costFuel.models.CostFuel import CostFuel
from api.costFuel.repositories.IRepositoryCostFuel import IRepositoryCostFuel
from django.shortcuts import get_object_or_404

class RepositoryCostFuel(IRepositoryCostFuel):
    """Implementation of the CostFuel repository interface."""
    
    def get_all(self) -> List[CostFuel]:
        """Returns all cost fuel records."""
        return CostFuel.objects.all()
    
    def get_by_id(self, id_fuel: int) -> Optional[CostFuel]:
        """Returns a cost fuel record by its ID."""
        try:
            return CostFuel.objects.get(id_fuel=id_fuel)
        except CostFuel.DoesNotExist:
            return None
    
    def get_by_order(self, order_key) -> List[CostFuel]:
        """Returns cost fuel records associated with an order."""
        return CostFuel.objects.filter(order__key=order_key)
    
    def get_by_truck(self, truck_id: int) -> List[CostFuel]:
        """Returns cost fuel records associated with a truck."""
        return CostFuel.objects.filter(truck__id_truck=truck_id)
    
    def create_cost_fuel(self, cost_fuel_data: Dict) -> CostFuel:
        """Creates a new cost fuel record."""
        return CostFuel.objects.create(**cost_fuel_data)
    
    def update_cost_fuel(self, id_fuel: int, cost_fuel_data: Dict) -> Optional[CostFuel]:
        """Updates an existing cost fuel record."""
        try:
            cost_fuel = CostFuel.objects.get(id_fuel=id_fuel)
            for key, value in cost_fuel_data.items():
                setattr(cost_fuel, key, value)
            cost_fuel.save()
            return cost_fuel
        except CostFuel.DoesNotExist:
            return None
    
    def delete_cost_fuel(self, id_fuel: int) -> bool:
        """Deletes a cost fuel record."""
        try:
            cost_fuel = CostFuel.objects.get(id_fuel=id_fuel)
            cost_fuel.delete()
            return True
        except CostFuel.DoesNotExist:
            return False