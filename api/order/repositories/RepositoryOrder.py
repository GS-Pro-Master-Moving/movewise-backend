from api.order.repositories.IRepositoryOrder import IRepositoryOrder
from api.order.models.Order import Order
from api.person.models import Person
from api.job.models import Job

class RepositoryOrder(IRepositoryOrder):
    @staticmethod
    def create_order(data):
        return Order.objects.create(**data)

    #edit order
    @staticmethod
    def update_order(order, data):
        # Verificar si la orden ya está finalizada
        if order.status == "Finalizada":
            raise Exception("No se pueden modificar órdenes finalizadas")
        
        # Manejo especial para `person`
        if "person" in data:
            person_data = data.pop("person")
            if isinstance(person_data, dict): #validando si es diccionario o una instancia
                person, _ = Person.objects.get_or_create(**person_data)
                order.person = person
            elif isinstance(person_data, Person): 
                order.person = person_data
        
        # Manejo especial para `job`
        if "job" in data:
            job_id = data.pop("job")
            try:
                order.job = Job.objects.get(id=job_id)  # Convertir el ID en una instancia de `Job`
            except Job.DoesNotExist:
                raise ValueError("El trabajo especificado no existe.")
        
        # Actualizar los demás campos
        for key, value in data.items():
            setattr(order, key, value)

        order.save()
        return order
    
