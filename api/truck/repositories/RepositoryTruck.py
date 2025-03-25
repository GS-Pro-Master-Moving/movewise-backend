from typing import List, Optional
from api.truck.models.Truck import Truck
from api.truck.repositories.IRepositoryTruck import IRepositoryTruck

class RepositoryTruck(IRepositoryTruck):

    def get_disponibles(self) -> List[Truck]:
        """Returns a list of available (active) trucks."""
        return Truck.objects.filter(status=True)

    def create_truck(self, number_truck: str, type: str, rol: str, name: str) -> Truck:
        """Creates a new truck."""
        return Truck.objects.create(
            number_truck=number_truck,
            type=type,
            rol=rol,
            name=name
        )

    def update_status(self, id_truck: int, status: bool) -> Optional[Truck]:
        """Activates or deactivates a truck."""
        try:
            truck = Truck.objects.get(id_truck=id_truck)
            truck.status = status
            truck.save()
            return truck
        except Truck.DoesNotExist:
            return None
