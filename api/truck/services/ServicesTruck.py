from typing import List, Optional, Dict
from api.truck.models.Truck import Truck
from api.truck.repositories.RepositoryTruck import RepositoryTruck
from api.truck.services.IServicesTruck import IServicesTruck
from api.company.models.Company import Company
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

class ServicesTruck(IServicesTruck):
    def __init__(self):
        self.repository = RepositoryTruck()

    def get_avaliable(self) -> List[Truck]:
        """Returns a list of available (active) trucks."""
        return self.repository.get_avaliable()

    def create_truck(self, truck_data: Dict, request) -> Truck:
        """
        Crea un Truck inyectando la Company extraída del token (request.company_id).
        """
        # Validate that the request has company_id
        if not hasattr(request, 'company_id'):
            raise ValidationError("Missing company context in the token")

        # Get the Company instance
        try:
            company = Company.objects.get(pk=request.company_id)
        except ObjectDoesNotExist:
            raise ValidationError("Invalid company in token")

        # Inject the FK into the data
        truck_data['id_company'] = company

        return self.repository.create_truck(truck_data)


    def update_status(self, id_truck: int, status: bool) -> Optional[Truck]:
        """Activates or deactivates a truck."""
        return self.repository.update_status(id_truck, status)
