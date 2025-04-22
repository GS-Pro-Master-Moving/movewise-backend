from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.assign.controllers.ControllerAssign import ControllerAssign
from api.costFuel.services.ServicesCostFuel import ServicesCostFuel
from api.order.serializers.OrderSerializer import OrderSerializer
from api.order.services.ServicesOrder import ServicesOrder  
from api.order.models.Order import Order
from api.job.models.Job import Job
from api.order.serializers.StatesSerializer import StatesUSASerializer
from api.order.models.Order import StatesUSA
from django.http import JsonResponse
from rest_framework.decorators import action
from api.workCost.services.ServicesWorkCost import ServicesWorkCost

class ControllerOrder(viewsets.ViewSet):
    """
    Controller for managing Order entities.

    Provides an endpoint for:
    - Getting a sumary of the cost in the order.
    - list all the orders.
    - Creating an order.
    - Partial update for some fields in order
    - Get all the states avaliable for the orders
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service = ServicesOrder()  
        self.workcost_service = ServicesWorkCost()

    def SumaryCost(self, request, pk=None):
        """
        Retrieves the summary of costs for a specific order.

        Returns:
        - 200 OK: A JSON object with the breakdown of costs and the total.
        - 404 Not Found: If the order does not exist.
        """
        workcost_service = ServicesWorkCost()
        cost_fuel_service = ServicesCostFuel()
        assign_service = ControllerAssign()
        try:
            # Retrieve the order by its primary key
            order = Order.objects.get(key=pk)

            # Expense
            expense = float(order.expense or 0)
            print("Expense:", expense)

            # Renting cost
            renting_cost = float(order.income or 0)
            print("Renting cost:", renting_cost)

            # Calculate fuel cost
            fuel_cost_list = cost_fuel_service.get_by_order(pk)
            total_fuel_cost = 0
            for fuel_cost in fuel_cost_list:
                total_fuel_cost += float(getattr(fuel_cost, 'cost_fuel', 0))
            print("Total fuel cost:", total_fuel_cost)

            # Calculate work cost
            work_cost_list = workcost_service.get_workCost_by_KeyOrder(pk)
            total_work_cost = 0
            for work_cost in work_cost_list:
                total_work_cost += float(getattr(work_cost, 'cost', 0))
            print("Total work cost:", total_work_cost)

            # Get assigned operators
            operators = assign_service.get_assigned_operators(pk)
            driver_salaries = 0.0
            other_salaries = 0.0

            # Sum the salaries
            for operator in operators.data:
                role = operator.get('rol', None)  # Getting the role field
                salary = float(operator.get('salary', 0))  # Parsing to float and getting the salary

                if role == 'driver':
                    driver_salaries += salary
                else:
                    other_salaries += salary

            # Print the results
            print("Driver salaries:", driver_salaries)
            print("Other salaries:", other_salaries)

            # Calculate the total cost
            total_cost = (
                expense +
                renting_cost +
                total_fuel_cost +
                total_work_cost +
                driver_salaries +
                other_salaries
            )
            print("Total cost:", total_cost)

            # Return the summary as a JSON response
            return Response({
                "status": "success",
                "data": {
                    "expense": expense,
                    "rentingCost": renting_cost,
                    "fuelCost": total_fuel_cost,
                    "workCost": total_work_cost,
                    "driverSalaries": driver_salaries,
                    "otherSalaries": other_salaries,
                    "totalCost": total_cost
                }
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Order not found",
                "messUser": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error calculating summary cost: {str(e)}",
                "messUser": f"Error calculating summary cost",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def list_all(self, request):
        """
        List all orders.

        Returns:
        - 200 OK: A list of all orders.
        """
        try:
            # Get all orders using the service
            orders = self.order_service.get_all_orders()
            # Return the response with the serialized data
            return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK) 
        
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders: {str(e)}",
                "messUser": f"Error in listing orders",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
            summary="Update status of an order and receives an evidence",
            description="Returns a list of all orders.",
            responses={200: OrderSerializer(many=True), 400: {"error": "Invalid data or evidence not found"}}
        )
    def update_status(self, request, pk=None):
        try:
            # Get the order by its key
            order = Order.objects.get(key=pk)
            #validation if the order status is finalized it cannot be updated
            if order.payStatus == 1:
                return Response({
                    "status": "error",
                    "messDev": "Order is finalized and cannot be modified",
                    "messUser": "Cannot edit finalized orders",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

            # Update the order using the service
            updated_order = self.order_service.update_status(request.data["url"], order)
            
            # Return the response with the updated data
            return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK) 
        
        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Order not found",
                "messUser": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating order: {str(e)}",
                "messUser": f"Error updating order",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary="Create a new order",
        description="Creates an order with the given data and returns the created entity.",
        request=OrderSerializer,
        responses={201: OrderSerializer, 400: {"error": "Invalid data"}}
    )
    def create(self, request):
        """
        Create a new order.

        Expects:
        - A JSON body with order details.

        Returns:
        - 201 Created: If the order is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = self.order_service.create_order(serializer.validated_data) 
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        
        # En caso de error, se envía un mensaje más detallado en inglés
        error_messages = serializer.errors
        detailed_error_message = f"Validation errors: {error_messages}"
        return Response({"error": detailed_error_message}, status=status.HTTP_400_BAD_REQUEST)

    # This decorator customizes the Swagger/OpenAPI documentation for this endpoint.
    # It defines a summary, a detailed description, the type of data expected in the request,
    # and possible response codes with their respective structures.
    @extend_schema(
        summary="Update an existing order",
        description="Updates an order with the given data if the order is not finalized.",
        request=OrderSerializer,
        responses={200: OrderSerializer, 400: {"error": "Invalid data"}, 403: {"error": "Cannot edit finalized order"}}
    )

    #actualizacion parcial --> permite actualizar solo algunos campos del modelo sin necesidad de enviar todos los datos
    #partial update --> allows you to update only some fields of the model without having to send all the data
    
    def partial_update(self, request, pk=None):
        try:
            # Get the order by its key
            order = Order.objects.get(key=pk)
            #validation if the order status is finalized it cannot be updated
            if order.payStatus == 1:
                return Response({
                    "status": "error",
                    "messDev": "Order is finalized and cannot be modified",
                    "messUser": "Cannot edit finalized orders",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

            # the job field is handled
            data = request.data.copy()
            if "job" in data and isinstance(data["job"], (int, str)):
                try:
                    # We just check that it exists, the conversion will be done by the service
                    Job.objects.get(id=data["job"])
                except Job.DoesNotExist:
                    return Response({
                        "status": "error",
                        "messDev": f"Job with ID {data['job']} does not exist",
                        "messUser": "El trabajo especificado no existe",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Update the order using the service
            updated_order = self.order_service.update_order(order, data)
            
            # Return the response with the updated data
            return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK) 
        
        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Order not found",
                "messUser": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating order: {str(e)}",
                "messUser": f"Error updating order",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get all states in USA",
        description="Returns a list of all states in USA.",
        responses={200: StatesUSASerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='states')
    def get_states(self, request):
        try:
            states = [{'code': state.value, 'name': state.label} for state in StatesUSA]
            return JsonResponse(states, safe=False)
        except Exception as e:
            error_response = {
                "status": "error",
                "messDev": f"Error fetching states: {str(e)}",
                "messUser": f"Error fetching states",
                "data": None
            }
            return JsonResponse(error_response, status=400)
        
    
