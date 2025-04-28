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
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, PermissionDenied

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
        try:
            company_id = request.company_id
            orders = self.order_service.get_all_orders(company_id)

            paginator = PageNumberPagination()
            paginated = paginator.paginate_queryset(orders, request)
            serialized = OrderSerializer(paginated, many=True)

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
            serialized_orders = OrderSerializer(paginated_orders, many=True)
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
        
    
