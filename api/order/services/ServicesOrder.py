from api.order.repositories.RepositoryOrder import RepositoryOrder
from api.order.services.IServicesOrder import IServicesOrder
from api.person.models.Person import Person  

from api.job.models.Job import Job

class ServicesOrder(IServicesOrder):
    def __init__(self):
        self.repository = RepositoryOrder()

    def get_all_orders(self):
        return self.repository.get_all_orders()
        
    def update_status(self, url, order):
        self.repository.update_status(url,order)
        return order
    
    def create_order(self, data):
        person_data = data.pop("person", None)  
        if person_data:
            person, _ = Person.objects.get_or_create(**person_data)
            data["person"] = person  

        return self.repository.create_order(data)
    
    def update_order(self, order, data):
        person_data = data.pop("person", None)
        if person_data:
            person, _ = Person.objects.get_or_create(**person_data)  
            order.person = person

        # Manejar el campo job
        if "job" in data:
            job_id = data.pop("job")
            try:
                order.job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise ValueError("El trabajo especificado no existe.")

        # Actualizar los demás campos
        for key, value in data.items():
            setattr(order, key, value)

        order.save()
        return order
    
    def get_states_usa(self):
      return [(state.value, state.label) for state in StatesUSA]
