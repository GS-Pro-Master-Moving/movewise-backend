from api.order.repositories.RepositoryOrder import RepositoryOrder
from api.order.services.IServicesOrder import IServicesOrder
from api.person.models.Person import Person  
from api.order.models.Order import Order  
from rest_framework.exceptions import ValidationError, PermissionDenied
from api.job.models.Job import Job

class ServicesOrder(IServicesOrder):
    def __init__(self):
        self.repository = RepositoryOrder()

    def get_all_orders(self, company_id):
        if not company_id:
            raise ValidationError("Company context missing")
        return self.repository.get_all_orders(company_id)
        
    def update_status(self, url, order):
        self.repository.update_status(url,order)
        return order
    
    def create_order(self, data):
        person_data = data.pop("person", None)  
        if person_data:
            person, _ = Person.objects.get_or_create(**person_data)
            data["person"] = person  

        return self.repository.create_order(data)
    
    def update_order(self, order, data: dict, request) -> Order:
        """
        Applies a partial update to `order` *only if* it belongs to
        request.company_id. Drops any 'person' key silently.
        """
        # Guard company context
        if not hasattr(request, 'company_id'):
            raise ValidationError("Company context missing")

        if order.id_company_id != request.company_id:
            raise PermissionDenied("You do not have permission to modify this order")

        # Drop person (we don’t update it here)
        data.pop("person", None)

        # Handle job
        if "job" in data:
            job_id = data.pop("job")
            try:
                order.job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise ValidationError("The specified job does not exist")

        # Apply other fields
        for key, val in data.items():
            setattr(order, key, val)

        order.save()
        return order
    
    def get_states_usa(self):
      return [(state.value, state.label) for state in StatesUSA]
