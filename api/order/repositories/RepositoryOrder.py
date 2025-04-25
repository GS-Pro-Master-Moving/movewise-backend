from api.order.repositories.IRepositoryOrder import IRepositoryOrder
from api.order.models.Order import Order
from api.person.models import Person
from api.job.models import Job
from api.order.models.Order import StatesUSA

class RepositoryOrder(IRepositoryOrder):
    @staticmethod
    def create_order(data):
        return Order.objects.create(**data)
    @staticmethod
    def update_status(url, order):
        # Verify if the order is finalized
        if order.payStatus == 1:
            raise Exception("Can't update a finalized order")

        print("url:", url)
        if url:
            order.evidence = url
        else:
            raise Exception("Evidence not found")
        
        print("Evidence found")
        
        # Update the status field
        order.status = "Finished"
        order.save()  # Save the changes to the database

        return order  # Return the updated order instance
    #edit order
    @staticmethod
    def update_order(order, data):
        # Verificar si la orden ya está finalizada
        if order.status == "Finished":
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
    
    @staticmethod
    def get_all_orders():
        return Order.objects.all()
    
    @staticmethod
    def get_states():
        return StatesUSA.objects.all()

    @staticmethod
    def delete_order_with_status(order_key):
        try:
            order = Order.objects.get(key=order_key)
            order.status = "Inactive"
            order.save()
            return order
        except Order.DoesNotExist:
            return f"Order {order_key} does not exist."