from api.order.models.Order import Order
from api.order.repositories.RepositoryOrder import RepositoryOrder
from api.order.services.IServicesOrder import IServicesOrder
from api.person.models.Person import Person  
from api.order.models.Order import Order  
from rest_framework.exceptions import ValidationError, PermissionDenied
from api.job.models.Job import Job
from api.workCost.services.ServicesWorkCost import ServicesWorkCost
from api.assign.services.ServicesAssign import ServicesAssign
from api.costFuel.services.ServicesCostFuel import ServicesCostFuel
from api.assign.serializers.SerializerAssign import AssignOperatorSerializer
from api.truck.serializers.SerializerTruck import SerializerTruck
from api.assign.models.Assign import Assign
from api.customerFactory.models.CustomerFactory import CustomerFactory
from django.shortcuts import get_object_or_404
import os
from django.core.files.storage import default_storage
from django.conf import settings
from api.company.models.Company import Company
from api.order.serializers.OrderSerializer import OrderSerializer
import logging

class ServicesOrder(IServicesOrder):
    def __init__(self):
        self.repository = RepositoryOrder()
    
    def get_all_orders_any_status(self, company_id, date_filter=None, status_filter=None, search_filter=None):
        if not company_id:
            raise ValidationError("Company context missing")
        
        return self.repository.get_all_orders_any_status(
            company_id=company_id,
            date_filter=date_filter,
            status_filter=status_filter,
            search_filter=search_filter
        )
    
    def get_all_orders(self, company_id):
        return self.repository.get_all_orders(company_id)
    
    def get_all_pending_orders(self, company_id):
        if not company_id:
            raise ValidationError("Company context missing")
        return self.repository.get_all_pending_orders(company_id)

    def get_all_orders_report(self, company_id):
        if not company_id:
            raise ValidationError("Company context missing")
        return self.repository.get_all_orders_report(company_id)
        
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
        if order.id_company_id != request.company_id:
            raise PermissionDenied("You do not have permission to modify this order.")

        for field in ['key_ref', 'date', 'distance', 'expense', 'income', 'weight', 'status']:
            if field in data:
                setattr(order, field, data[field])

        if "job" in data:
            job = get_object_or_404(Job, id=data["job"])
            order.job = job
        
        order.save()
        
        return order

    def get_states_usa(self):
        return [(state.value, state.label) for state in StatesUSA]

    def calculate_summary(self, order_key):
        """
        Calculates the summary of costs for a specific order.

        Args:
        - order_key: The key of the order.

        Returns:
        - A dictionary containing the breakdown of costs and the total.
        """
        cost_fuel_service = ServicesCostFuel()
        workcost_service = ServicesWorkCost()
        assign_service = ServicesAssign()
        try:
            # Retrieve the order by its primary key
            order = Order.objects.get(key=order_key)
            if order.customer_factory:
                customer_factory = order.customer_factory.id_factory
            else:
                customer_factory = None 

            # Expense
            expense = float(order.expense or 0)

            # Renting cost
            renting_cost = float(order.income or 0)

            # Calculate fuel cost
            fuel_cost_list = cost_fuel_service.get_by_order(order_key)
            total_fuel_cost = sum(float(getattr(fuel_cost, 'cost_fuel', 0)) for fuel_cost in fuel_cost_list)

            # Calculate work cost
            work_cost_list = workcost_service.get_workCost_by_KeyOrder(order_key)
            total_work_cost = sum(float(getattr(work_cost, 'cost', 0)) for work_cost in work_cost_list)

            # Get assigned operators and calculate salaries
            assigned_operators = assign_service.get_assigned_operators(order_key)
            driver_salaries = 0.0
            other_salaries = 0.0

            for assignment in assigned_operators:
                operator = assignment.operator
                role = assignment.rol  # Get the role from the Assign model
                salary = float(operator.salary or 0)
                if role == 'driver':
                    driver_salaries += salary
                else:
                    other_salaries += salary

            # Calculate the total cost
            total_cost = (
                expense +
                renting_cost +
                total_fuel_cost +
                total_work_cost +
                driver_salaries +
                other_salaries
            )

            # Return the summary as a dictionary
            return {
                "expense": expense,
                "rentingCost": renting_cost,
                "fuelCost": total_fuel_cost,
                "workCost": total_work_cost,
                "driverSalaries": driver_salaries,
                "otherSalaries": other_salaries,
                "customer_factory": customer_factory,
                "totalCost": total_cost,
            }

        except Order.DoesNotExist:
            raise ValueError("Order not found")
            
    def delete_order_with_status(self, order_key):
        """
        Deletes an order if its status is "Finished".

        Args:
        - order_key: The key of the order to be deleted.

        Returns:
        - A message indicating the result of the operation.
        """
        return self.repository.delete_order_with_status(order_key)
    
    
    def _validate_company_context(self, request):
        """
        Validates that the request has a valid company context.
        
        Args:
            request: The HTTP request object
            
        Raises:
            ValidationError: If company context is missing
        """
        if not getattr(request, 'company_id', None):
            raise ValidationError("Company context is required")

    def _validate_person_id(self, data):
        """
        Validates that person_id is present in the data.
        
        Args:
            data: Dictionary containing the request data
            
        Raises:
            ValidationError: If person_id is missing
        """
        if 'person_id' not in data:
            raise ValidationError("person_id is required")

    def _get_company(self, request):
        """
        Retrieves the company object from the request context.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Company: The company instance
            
        Raises:
            ValidationError: If company doesn't exist
        """
        try:
            return Company.objects.get(pk=request.company_id)
        except Company.DoesNotExist:
            raise ValidationError("Invalid company context")

    def _get_person(self, data, company):
        """
        Retrieves the person object by ID within the company context.
        
        Args:
            data: Dictionary containing person_id
            company: Company instance
            
        Returns:
            Person: The person instance
            
        Raises:
            ValidationError: If person doesn't exist in the company
        """
        try:
            return Person.objects.get(id_person=data['person_id'], id_company=company)
        except Person.DoesNotExist:
            raise ValidationError("Person not found in company")

    def _get_or_create_workhouse_job(self, company):
        """
        Gets or creates a 'workhouse' job type for the company.
        
        Args:
            company: Company instance
            
        Returns:
            Job: The workhouse job instance
        """
        return Job.objects.get_or_create(
            name='workhouse',
            id_company=company,
            defaults={'state': True}  # Job activo por defecto
        )[0]

    def _build_person_data_for_serializer(self, person):
        """
        Builds person data dictionary for the serializer.
        
        Args:
            person: Person instance
            
        Returns:
            dict: Person data dictionary
        """
        return {
            'id_person': person.id_person,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'phone': person.phone,
            'email': person.email,
            'address': person.address,
            # Agrega otros campos de Person que necesites según tu modelo
        }

    def _generate_workhouse_key_ref(self, company_id):
        """
        Generates the next workhouse key reference.
        
        Args:
            company_id: ID of the company
            
        Returns:
            str: Formatted key reference (e.g., 'WH-0001')
        """
        next_number = self.repository.get_next_workhouse_number(company_id)
        return f'WH-{next_number:04d}'  # Formato: WH-0001, WH-0002, etc.

    def _prepare_workhouse_order_data(self, data, company, person, job):
        """
        Prepares the order data for workhouse creation.
        
        Args:
            data: Original request data
            company: Company instance
            person: Person instance
            job: Job instance
            
        Returns:
            dict: Prepared order data for serializer
        """
        # Preparar los datos para el serializer
        order_data = data.copy()
        
        # Convertir person_id a los datos de persona que espera el serializer
        order_data['person'] = self._build_person_data_for_serializer(person)
        
        # Establecer el job automáticamente
        order_data['job'] = job.id
        
        # Generar key_ref automáticamente para workhouse
        order_data['key_ref'] = self._generate_workhouse_key_ref(company.id)
        
        # Asegurar status por defecto
        order_data['status'] = order_data.get('status', 'Pending')
        
        # Remover person_id ya que no es parte del modelo
        order_data.pop('person_id', None)
        
        return order_data

    def _create_order_via_serializer(self, order_data, request, company):
        """
        Creates an order using the OrderSerializer.
        
        Args:
            order_data: Prepared order data
            request: HTTP request object
            company: Company instance
            
        Returns:
            Order: Created order instance
            
        Raises:
            ValidationError: If serializer validation fails
        """
        serializer = OrderSerializer(
            data=order_data,
            context={'request': request, 'company_id': company.id}
        )
        
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        return serializer.save()

    # ====== SERVICIOS PRINCIPALES PARA WORKHOUSE ======

    def create_workhouse_order(self, data, request):
        """
        Creates a workhouse order using the serializer approach.
        Automatically handles job creation/retrieval and person lookup.
        
        Args:
            data: Request data containing order information
            request: HTTP request object
            
        Returns:
            Order: Created workhouse order instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validaciones iniciales
        self._validate_company_context(request)
        self._validate_person_id(data)
        
        # Obtener recursos
        company = self._get_company(request)
        person = self._get_person(data, company)
        job = self._get_or_create_workhouse_job(company)
        
        # Preparar datos para el serializer
        order_data = self._prepare_workhouse_order_data(data, company, person, job)
        
        # Crear orden usando el serializer
        return self._create_order_via_serializer(order_data, request, company)
    
    def get_all_workhouse_orders(self, company_id):
        """
        Get all workhouse orders for a company.
        
        Workhouse orders are identified by:
        - job.name = 'workhouse' OR
        - key_ref starting with 'WH-'
        
        Args:
        - company_id: ID of the company
        
        Returns:
        - QuerySet of workhouse orders
        """
        if not company_id:
            raise ValidationError("Company context missing")
        
        return self.repository.get_all_workhouse_orders(company_id)