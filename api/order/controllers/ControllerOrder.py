from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.costFuel.serializers.SerializerCostFuel import SerializerCostFuel
from api.assign.models.Assign import Assign
from api.costFuel.services.ServicesCostFuel import ServicesCostFuel
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.order.serializers.OrderSerializer import OrderSerializer
from api.order.services.ServicesOrder import ServicesOrder  
from api.order.models.Order import Order
from api.job.models.Job import Job
from api.order.serializers.StatesSerializer import StatesUSASerializer
from api.order.models.Order import StatesUSA
from django.http import JsonResponse
from rest_framework.decorators import action, parser_classes
from api.truck.models.Truck import Truck
from api.workCost.services.ServicesWorkCost import ServicesWorkCost
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from api.order.serializers.SerializerOrderEvidence import SerializerOrderEvidence

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
        try:
            company_id = request.company_id
            orders = self.order_service.get_all_orders(company_id)

            paginator = PageNumberPagination()
            paginated = paginator.paginate_queryset(orders, request)
            serialized = OrderSerializer(paginated, many=True, context={'request': request})

            return Response({
                "status": "success",
                "messDev": f"Orders listed successfully. Current company id: {company_id}",
                "messUser": "Orders listed successfully",
                "current_company_id": company_id,
                "data": paginator.get_paginated_response(serialized.data).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders: {e}",
                "messUser": "Error in listing orders",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def list_with_fuel(self, request):
        """
        Endpoint to list all orders paginated (10 per page) including detailed gasoline cost entries.
        """
        try:
            # Obtener company_id del request
            company_id = request.company_id

            # Obtener órdenes filtradas por empresa
            orders = self.order_service.get_all_orders(company_id)

            # Paginación
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)

            # Serialización
            serialized_orders = OrderSerializer(paginated_orders, many=True, context={'request': request})
            orders_data = serialized_orders.data

            # Instanciar servicio de CostFuel
            cost_fuel_service = ServicesCostFuel()

            for order_data in orders_data:
                # Eliminar campos innecesarios
                order_data.pop('expense', None)
                order_data.pop('income', None)
                order_data.pop('payStatus', None)

                # Buscar fuel entries de la orden
                key = order_data.get('key')
                fuel_entries = cost_fuel_service.get_by_order(key)

                # Formatear la lista de costos de combustible
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

                # Agregar fuelCost a la orden
                order_data['fuelCost'] = fuel_list

            # Respuesta paginada personalizada
            return Response({
                "status": "success",
                "messDev": f"Orders with fuel listed successfully. Current company id: {company_id}",
                "messUser": "Orders listed successfully",
                "current_company_id": company_id,
                "data": paginator.get_paginated_response(orders_data).data
            }, status=status.HTTP_200_OK)

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
        print("\n=== STARTING ORDER CREATION ===")
        print("Request headers:", request.headers)
        print("Request data:", request.data)
        
        serializer = OrderSerializer(
            data=request.data,
            context={'request': request}  # IMPORTAN SEND CONTEXT
        )
        
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = serializer.save()
            print("Order created successfully:", order.key)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Critical error:", str(e))
            return Response(
                {"error": f"Error creating order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # This decorator customizes the Swagger/OpenAPI documentation for this endpoint.
    # It defines a summary, a detailed description, the type of data expected in the request,
    # and possible response codes with their respective structures.
    @extend_schema(
        summary="Update an existing order",
        description="Updates an order with the given data if the order is not finalized.",
        request=OrderSerializer,
        responses={200: OrderSerializer, 400: {"error": "Invalid data"}, 403: {"error": "Cannot edit finalized order"}}
    )

    #partial update --> allows you to update only some fields of the model without having to send all the data
    def partial_update(self, request, pk=None):
        """
        PATCH /orders/{key}/
        """
        #Fetch
        try:
            order = Order.objects.get(key=pk)
        except Order.DoesNotExist:
            return Response(..., status=status.HTTP_404_NOT_FOUND)

        # Block finalized
        if order.payStatus == 1:
            return Response(..., status=status.HTTP_403_FORBIDDEN)

        # Pre-validate job
        if "job" in request.data:
            try:
                Job.objects.get(id=request.data["job"])
            except Job.DoesNotExist:
                return Response(..., status=status.HTTP_400_BAD_REQUEST)

        # Delegate to service
        try:
            updated = ServicesOrder().update_order(order, request.data.copy(), request)
            return Response({
                "status": "success",
                "messDev": "Order updated successfully",
                "messUser": "Order updated",
                "data": OrderSerializer(updated).data
            }, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({
                "status": "error",
                "messDev": str(ve),
                "messUser": "Invalid data",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as pd:
            return Response({
                "status": "error",
                "messDev": str(pd),
                "messUser": "Permission denied",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating order: {e}",
                "messUser": "There was an error updating the order",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            
    @extend_schema(
        summary="Get an order by ID with its operators, trucks, and cost fuel",
        description="Returns a detailed order with its operators, trucks, and cost fuel.",
        responses={200: StatesUSASerializer(many=True)}
    )
    def get_order_details(self, request, pk=None):
        """
        Get an order by ID with its operators, trucks, and cost fuel.

        Returns:
        - 200 OK: A detailed order with its operators, trucks, and cost fuel.
        - 404 Not Found: If the order does not exist.
        """
        # Services
        cost_fuel_service = ServicesCostFuel()
        try:
            # Retrieve the order by its primary key
            order = Order.objects.get(key=pk)
            
            # Retrieve the operators in the order 
            assigned_operators = Assign.objects.filter(order__key=pk).select_related('operator')
            print("Assigned Operators:", assigned_operators)
            # Retrieve the trucks in the order
            assigned_trucks = Truck.objects.filter(assignments__order__key=pk).distinct()
            print("Assigned Trucks:", assigned_trucks)
            # Retrieve the cost fuel in the order
            cost_fuel = cost_fuel_service.get_by_order(pk)
            print("Cost Fuel:", cost_fuel)
            # Serialize the order data
            serialized_order = OrderSerializer(order, context={'request': request})
            # Serialize the cost fuel data
            serialized_cost_fuel = SerializerCostFuel(cost_fuel, many=True)
            # Serualize the assigned operators data
            serialized_operators = SerializerOperator(
                [op.operator for op in assigned_operators], many=True
            )
            
            
            # Prepare the response data
            response = {
                "order": serialized_order.data,
                "assigned_operators": serialized_operators.data,
                "cost_fuel": serialized_cost_fuel.data,
                "assigned_trucks": assigned_trucks
            }
            # Return the detailed order as a JSON response
            return Response(response, status=status.HTTP_200_OK)
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
                "messDev": f"Error fetching order details: {str(e)}",
                "messUser": "Error fetching order details",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    @extend_schema(
        summary="Update status of an order for elimination",
        description="Update the status of an order.",
        responses={200: OrderSerializer(many=True), 400: {"error": "Invalid data or evidence not found"}}
    )
    def delete_order_with_status(self, request, pk=None):
        try:
            # Get the order by its key
            order = Order.objects.get(key=pk)
            #validation if the order status is finalized it cannot be updated
            if order.status == "Inactive":
                return Response({
                    "status": "error",
                    "messDev": "Order is deleted and cannot be modified",
                    "messUser": "Cannot edit deleted orders",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

            # Update the order using the service
            result = self.order_service.delete_order_with_status(pk)
            
            # Return the response with the updated data
            return Response(result, status=status.HTTP_200_OK) 
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
        summary="List the orders that are Pending",
        description="List just the orders that are pending.",
        responses={200: OrderSerializer(many=True), 400: {"error": "Unexpected error"}}
    )
    def list_pending_orders(self, request):
        try:
            # Get all orders using the service
            orders = self.order_service.get_all_orders()

            # Filter the orders to get only those with status "Pending"
            pending_orders = [order for order in orders if order.status == "Pending"]

            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(pending_orders, request)

            # Serialize the paginated data
            serialized_orders = OrderSerializer(paginated_orders, many=True, context={'request': request})

            # Return the paginated response
            return paginator.get_paginated_response(serialized_orders.data)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching pending orders: {str(e)}",
                "messUser": "Error fetching pending orders",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
    summary="Update order evidence",
    description="Updates the evidence image for an order. Accepts multipart/form-data with an image file.",
    request={
        'multipart/form-data': SerializerOrderEvidence
    },
    responses={200: SerializerOrderEvidence}
    )
    @parser_classes([MultiPartParser, FormParser])
    def update_evidence(self, request, pk):
        try:
            order = Order.objects.get(key=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if there's a file in the request
        if 'evidence' not in request.FILES:
            return Response(
                {
                    "message": "Validation error",
                    "errors": {"evidence": ["No file was submitted."]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete old file if exists
        if order.evidence:
            order.evidence.delete(save=False)

        # Update with new file
        order.evidence = request.FILES['evidence']
        
        # IMPORTANT: Only update the evidence field to prevent affecting dispatch_ticket
        order.save(update_fields=['evidence'])

        # Serialize and return response
        serializer = SerializerOrderEvidence(order, context={'request': request})
        return Response(
            {
                "message": "Evidence updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )