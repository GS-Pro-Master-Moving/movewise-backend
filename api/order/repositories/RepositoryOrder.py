from api.order.repositories.IRepositoryOrder import IRepositoryOrder
from api.order.models.Order import Order
from api.person.models import Person
from api.job.models import Job
from api.order.models.Order import StatesUSA
from django.db.models import Max 
import datetime
from django.db.models import Q
from django.db.models.functions import TruncDay
from django.db.models import Count
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
    def get_all_orders_any_status(self, company_id, date_filter=None, status_filter=None, search_filter=None, location_filter=None):
        # Consulta base
        queryset = Order.objects.filter(id_company_id=company_id)
        
        if date_filter:
            try:
                # Convertir string a fecha usando datetime y luego extraer solo la fecha
                from datetime import datetime
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(date=filter_date)
            except ValueError:
                # Si la fecha no es válida, ignorar el filtro
                pass
        
        if status_filter:
            # Normalizar el status para comparación case-insensitive
            queryset = queryset.filter(status__iexact=status_filter)
        
        if search_filter:
            search_q = Q(key_ref__icontains=search_filter) | \
                    Q(person__first_name__icontains=search_filter) | \
                    Q(person__last_name__icontains=search_filter)
            queryset = queryset.filter(search_q)
        
        if location_filter:
            # Filtrar por ubicación (state_usa)
            queryset = queryset.filter(state_usa__icontains=location_filter)
        
        # Ordenar por fecha descendente para mostrar más recientes primero
        return queryset.order_by('-date', '-key')
    
    def get_all_orders(self, company_id):
        return Order.objects.filter(id_company_id=company_id)
    
    def get_all_pending_orders(self, company_id):
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
        
    def get_next_workhouse_number(self, company_id):
        """
        Generates the next workhouse order number for a company.
        Returns an integer that will be formatted as WH-XXXX
        """
        from django.db.models import Max
        import re
        
        # Get the last workhouse order number
        last_order = Order.objects.filter(
            id_company_id=company_id,
            key_ref__startswith='WH-'
        ).aggregate(Max('key_ref'))['key_ref__max']
        
        if last_order:
            try:
                # Extract number from WH-XXXX format
                match = re.search(r'WH-(\d+)', last_order)
                if match:
                    return int(match.group(1)) + 1
                else:
                    return 1
            except (ValueError, AttributeError):
                return 1
        
        return 1

    def create_workhouse_order(self, validated_data):
        return Order.objects.create(**validated_data)

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
        
    def update_payments_by_key_ref(self, key_ref, expense, income):
        orders = Order.objects.filter(key_ref=key_ref)
        count = orders.count()
        if count == 0:
            return None
        expense_per_order = expense / count
        income_per_order = income / count
        updated_orders = []
        for order in orders:
            order.expense = expense_per_order
            order.income = income_per_order
            order.payStatus = 1
            order.save(update_fields=['expense', 'income', 'payStatus'])
            updated_orders.append(order)
        return updated_orders
    
    def get_orders_by_key_ref(self, key_ref):
        """
        Get all orders by key_ref.

        Args:
        - key_ref: The key reference to filter orders
        Returns:
        - QuerySet of orders matching the key_ref
        """
        return Order.objects.filter(key_ref=key_ref).order_by('-date')
    
    def count_orders_per_day_in_month(self, company_id, year, month):
        """
        Returns a list of dicts with 'date' and 'count' for each day with orders in the given month.
        """
        return (
            Order.objects
            .filter(id_company_id=company_id, date__year=year, date__month=month)
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(count=Count('key'))
            .order_by('day')
        )
        
    def filter_by_location(self, company_id, country=None, state=None, city=None):
        """
        Filtra órdenes por país, estado y ciudad usando el campo state_usa.
        """
        qs = Order.objects.filter(id_company_id=company_id)
        if country:
            qs = qs.filter(state_usa__istartswith=country)
        if state:
            qs = qs.filter(state_usa__icontains=f", {state}")
        if city:
            qs = qs.filter(state_usa__icontains=f", {city}")
        return qs