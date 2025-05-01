from typing import List, Optional, Dict
from api.truck.models.Truck import Truck
from api.truck.repositories.IRepositoryTruck import IRepositoryTruck

class RepositoryTruck(IRepositoryTruck):

    def get_avaliable(self, company_id) -> List[Truck]:
        """
        Returns a list of available (active) trucks for a specific company.
        """
        return Truck.objects.filter(status=True, id_company_id=company_id)

    def create_truck(self, truck_data: Dict) -> Truck:
        """Creates a new truck using a dictionary of data."""
        return Truck.objects.create(**truck_data)

    def update_status(self, id_truck: int, status: bool) -> Optional[Truck]:
        """Activates or deactivates a truck."""
        try:
            truck = Truck.objects.get(id_truck=id_truck)
            truck.status = status
            truck.save()
            return truck
        except Truck.DoesNotExist:
            return None
