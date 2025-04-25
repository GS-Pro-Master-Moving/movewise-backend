from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.costFuel.serializers.SerializerCostFuel import SerializerCostFuel
from api.assign.models.Assign import Assign
from api.assign.services.ServicesAssign import ServicesAssign
from api.costFuel.services.ServicesCostFuel import ServicesCostFuel
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.order.serializers.OrderSerializer import OrderSerializer
from api.order.services.ServicesOrder import ServicesOrder  
from api.order.models.Order import Order
from api.job.models.Job import Job
from api.order.serializers.StatesSerializer import StatesUSASerializer
from api.order.models.Order import StatesUSA
from django.http import JsonResponse
from rest_framework.decorators import action
from api.truck.models.Truck import Truck
from api.workCost.services.ServicesWorkCost import ServicesWorkCost
from rest_framework.pagination import PageNumberPagination

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
        try:
            # Use the service to calculate the summary
            summary = self.order_service.calculate_summary(pk)

            # Return the summary as a JSON response
            return Response({
                "status": "success",
                "data": summary
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                "status": "error",
                "messDev": str(e),
                "messUser": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error calculating summary cost: {str(e)}",
                "messUser": "Error calculating summary cost",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    def list_all(self, request):
        """
        List all orders with pagination.

        Returns:
        - 200 OK: A paginated list of all orders.
        """
        try:
            # Get all orders using the service
            orders = self.order_service.get_all_orders()

            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)

            # Serialize the paginated data
            serialized_orders = OrderSerializer(paginated_orders, many=True)

            # Return the paginated response
            return paginator.get_paginated_response(serialized_orders.data)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders: {str(e)}",
                "messUser": "Error in listing orders",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def list_with_fuel(self, request):
        """
        Endpoint to list all orders paginated (10 per page) including detailed gasoline cost entries.
        """
        try:
            orders = self.order_service.get_all_orders()
            paginator = PageNumberPagination()
            paginated = paginator.paginate_queryset(orders, request)

            serialized = OrderSerializer(paginated, many=True)
            orders_data = serialized.data

            cost_fuel_service = ServicesCostFuel()
            for order_data in orders_data:
                # Remove unnecessary fields
                order_data.pop('expense', None)
                order_data.pop('income', None)
                order_data.pop('payStatus',None)

                key = order_data.get('key')
                fuel_entries = cost_fuel_service.get_by_order(key)
                fuel_list = []
                for fe in fuel_entries:
                    truck = fe.truck
                    fuel_list.append({
                        'id_fuel': fe.id_fuel,
                        'cost_fuel': fe.cost_fuel,
                        'cost_gl': fe.cost_gl,
                        'fuel_qty': fe.fuel_qty,
                        'distance': fe.distance,
                        'truck': {
                            'id_truck': truck.id_truck,
                            'number_truck': truck.number_truck,
                            'type': truck.type,
                            'name': truck.name,
                            'status': truck.status,
                            'category': truck.category,
                        }
                    })
                order_data['fuelCost'] = fuel_list

            return paginator.get_paginated_response(orders_data)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders with fuel cost: {e}",
                "messUser": "Error fetching orders with fuel cost",
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
    def summary_orders_list(self, request):
        """
        Retrieves a paginated list of orders with a summary of costs.

        Returns:
        - 200 OK: A JSON object with the paginated list of orders and their respective summaries.
        - 400 Bad Request: If an error occurs.
        """
        try:
            # Get all orders using the service
            orders = self.order_service.get_all_orders()

            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)

            # Prepare the response data
            orders_summary = []
            for order in paginated_orders:
                # Extract the required fields
                order_data = {
                    "key": order.key,
                    "key_ref": order.key_ref,
                    "client": order.person.first_name + " " + order.person.last_name,
                    "date": order.date,
                    "state": order.state_usa,
                }

                # Calculate the summary for the order using the service
                order_data["summary"] = self.order_service.calculate_summary(order.key)

                # Append the order data to the response list
                orders_summary.append(order_data)

            # Return the paginated response
            return paginator.get_paginated_response(orders_summary)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders with summaries: {str(e)}",
                "messUser": "Error fetching orders with summaries",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)