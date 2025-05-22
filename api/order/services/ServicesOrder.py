
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

class ServicesOrder(IServicesOrder):
    def __init__(self):
        self.repository = RepositoryOrder()
    
    def get_all_orders_any_status(self, company_id):
        if not company_id:
            raise ValidationError("Company context missing")
        return self.repository.get_all_orders_any_status(company_id)
    
    def get_all_orders(self, company_id):
        if not company_id:
            raise ValidationError("Company context missing")
        return self.repository.get_all_orders(company_id)

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
    
    #servicios nuevos para workhouse

    def create_workhouse_order(self, data, request):
        """
        Creates a workhouse order with auto-generated key_ref and workhouse job type.
        
        Args:
        - data: Order data from request (debe incluir person_id)
        - request: HTTP request object containing company context
        
        Returns:
        - Created Order instance
        
        Raises:
        - ValueError: Si falta person_id, la persona no existe o no pertenece a la compañía
        """
        if not hasattr(request, 'company_id') or not request.company_id:
            raise ValueError("Company context missing")
        
        try:
            from api.company.models.Company import Company
            from api.person.models import Person 
            
            # Get company
            company = Company.objects.get(pk=request.company_id)
            
            # Find or create workhouse job
            workhouse_job, created = Job.objects.get_or_create(
                name='workhouse',
                defaults={'description': 'Workhouse job type'}
            )
            
            # Generate auto-incremental key_ref para workhouse
            next_wh_number = self.repository.get_next_workhouse_number()
            key_ref = f"WH-{next_wh_number:05d}"  # Formato: WH-00001, WH-00002, etc.
            
            # Obtener person_id del request
            person_id = data.pop("person_id", None)
            if not person_id:
                raise ValueError("person_id is required for creating a workhouse order")
             
            # Obtener customer_factory_id si existe
            customer_factory_id = data.pop("customer_factory", None)  # Asume que el request envía "customer_factory" con el ID
            customer_factory = None
            if customer_factory_id:
                customer_factory = CustomerFactory.objects.get(
                    id_factory=customer_factory_id, 
                )

            # Validar que la persona existe y pertenece a la compañía
            try:
                person = Person.objects.get(id_person=person_id, id_company=company)
            except Person.DoesNotExist:
                raise ValueError("Person not found or does not belong to the company")
            
            # Crear orden
            order_data = {
                'id_company': company,
                'person': person,
                'job': workhouse_job,
                'key_ref': key_ref,
                'customer_factory': customer_factory,
                **data
            }
            
            # Asegurar que el job sea workhouse (sobrescribe si viene en data)
            order_data['job'] = workhouse_job
            
            return self.repository.create_workhouse_order(order_data)
            
        except Job.DoesNotExist:
            raise ValueError("Workhouse job type could not be created")
        except Company.DoesNotExist:
            raise ValueError("Company not found")
        except Exception as e:
            raise ValueError(f"Error creating workhouse order: {str(e)}")
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
        