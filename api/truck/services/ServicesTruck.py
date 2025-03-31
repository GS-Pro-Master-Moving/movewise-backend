from typing import List, Optional, Dict
from api.truck.models.Truck import Truck
from api.truck.repositories.RepositoryTruck import RepositoryTruck
from api.truck.services.IServicesTruck import IServicesTruck

class ServicesTruck(IServicesTruck):
    def __init__(self):
        self.repository = RepositoryTruck()

    def get_avaliable(self) -> List[Truck]:
        """Returns a list of available (active) trucks."""
        return self.repository.get_avaliable()

    def create_truck(self, truck_data: Dict) -> Truck:
        """Creates a new truck with the given data."""
        return self.repository.create_truck(truck_data)

    def update_status(self, id_truck: int, status: bool) -> Optional[Truck]:
        """Activates or deactivates a truck."""
        return self.repository.update_status(id_truck, status)
