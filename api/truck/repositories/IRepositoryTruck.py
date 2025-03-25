from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from api.truck.models.Truck import Truck

class IRepositoryTruck(ABC):

    @abstractmethod
    def get_disponibles(self) -> List[Truck]:
        """Returns a list of available (active) trucks."""
        pass

    @abstractmethod
    def create_truck(self, truck_data: Dict) -> Truck:
        """Creates a new truck."""
        pass

    @abstractmethod
    def update_status(self, id_truck: int, status: bool) -> Optional[Truck]:
        """Activates or deactivates a truck."""
        pass
