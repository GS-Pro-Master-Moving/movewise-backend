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
    
    # @staticmethod
    #retornar todas las ordenes de una company sin importar el status
    def get_all_orders_any_status(self, company_id):
        return Order.objects.filter(id_company_id=company_id)

    def get_all_orders(self, company_id):
        return Order.objects.filter(id_company_id=company_id, status='pending')
    
    def get_all_orders_report(self, company_id):
        return Order.objects.filter(id_company_id=company_id)
    
    @staticmethod
    def get_states():
        return StatesUSA.objects.all()

    @staticmethod
    def delete_order_with_status(order_key):
        try:
            order = Order.objects.get(key=order_key)
            order.status = "Inactive"
            order.save()
            if(order.status == "Inactive"):
                return f"Order deleted successfully. status: {order.status}"
            else:
                return f"Order could not be deleted. status: {order.status}"
        except Order.DoesNotExist:
            return f"Order does not exist."
        
    #metodos nuevos para workhouse

    def create_workhouse_order(self, data):
        """
        Creates a workhouse order in the database.
        
        Args:
        - data: Dictionary containing order data
        
        Returns:
        - Created Order instance
        """
        return Order.objects.create(**data)

    def get_next_workhouse_number(self):
        """
        Gets the next sequential number for workhouse key_ref.
        
        Returns:
        - Integer representing the next workhouse number
        """
        # Get the latest workhouse order by key_ref
        latest_workhouse = Order.objects.filter(
            key_ref__startswith='WH-'
        ).order_by('-key_ref').first()
        
        if latest_workhouse:
            # Extract number from key_ref (e.g., 'WH-00001' -> 1)
            try:
                current_number = int(latest_workhouse.key_ref.split('-')[1])
                return current_number + 1
            except (IndexError, ValueError):
                # If there's an issue parsing, start from 1
                return 1
        else:
            # No workhouse orders exist yet
            return 1

    def get_all_workhouse_orders(self, company_id):
        """
        Get all workhouse orders for a specific company.
        
        Workhouse orders are identified by:
        - job.name = 'workhouse' OR
        - key_ref starting with 'WH-'
        
        Args:
        - company_id: ID of the company
        
        Returns:
        - QuerySet of workhouse orders
        """
        from django.db.models import Q
        
        return Order.objects.filter(
            id_company_id=company_id
        ).filter(
            Q(job__name='workhouse') | Q(key_ref__startswith='WH-')
        ).distinct().order_by('-date')