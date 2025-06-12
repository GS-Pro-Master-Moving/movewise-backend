import traceback
import logging

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
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from api.utils.s3utils import upload_evidence_file
from api.utils.image_processor import ImageProcessor
from datetime import datetime, timedelta

# Configuración de logging
logger = logging.getLogger(__name__)

class ControllerOrder(viewsets.ViewSet):
    lookup_field = 'key'
    parser_classes = (JSONParser, MultiPartParser, FormParser)

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

    def handle_error(self, exc):
        """Manejador centralizado de errores"""
        if isinstance(exc, ValidationError):
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, PermissionDenied):
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.exception("Internal server error")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
    
    @extend_schema(
        summary="List all orders with all status",
        description="Returns a list of all orders.",
        responses={200: OrderSerializer(many=True)}
    )
    def list_all_status(self, request):
        try:
            company_id = request.company_id
            
            # Extraer parámetros de filtro opcionales
            date_filter = request.GET.get('date', None)
            status_filter = request.GET.get('status', None)
            search_filter = request.GET.get('search', None)
            
            print(f"fecha recibida: {date_filter}")
            # Obtener órdenes con filtros opcionales
            orders = self.order_service.get_all_orders_any_status(
                company_id=company_id,
                date_filter=date_filter,
                status_filter=status_filter,
                search_filter=search_filter
            )

            paginator = PageNumberPagination()
            paginated = paginator.paginate_queryset(orders, request)
            serialized = OrderSerializer(paginated, many=True, context={'request': request})

            return Response({
                "status": "success",
                "messDev": f"Orders listed successfully. Current company id: {company_id}. Filters applied: date={date_filter}, status={status_filter}, search={search_filter}",
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
    
    @extend_schema(
        summary="List all orders ",
        description="Returns a list of all orders.",
        responses={200: OrderSerializer(many=True)}
    )
    def list_all(self, request):
        try:
            company_id = request.company_id
            orders = self.order_service.get_all_pending_orders(company_id)

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
        
    
    @extend_schema(
    summary="List all orders with their assigned operators and cost summary",
    description="Returns a list of all orders with detailed information about assigned operators and cost summary.",
    responses={200: OrderSerializer(many=True)}
    )
    def list_orders_with_operators_and_summary(self, request):
        """
        Lists all orders with their assigned operators' information and cost summary.
        
        Returns:
        - 200 OK: A JSON object containing the paginated list of orders with operators and cost summary.
        - 400 Bad Request: If an error occurs during processing.
        """
        try:
            company_id = request.company_id
            orders = self.order_service.get_all_pending_orders(company_id)

            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)
            
            result = []
            
            for order in paginated_orders:
                # Get operators assigned to this order
                assigned_operators = Assign.objects.filter(order__key=order.key).select_related(
                    'operator', 
                    'operator__person'
                )
                
                # Serialize order data
                order_data = OrderSerializer(order, context={'request': request}).data
                
                # Calculate the summary for this order using the existing service method
                summary_data = self.order_service.calculate_summary(order.key)
                
                # Serialize assigned operators
                operators_data = []
                for assignment in assigned_operators:
                    operator_data = {
                        'id_assign': assignment.id,
                        'operator_id': assignment.operator.id_operator,
                        'code': assignment.operator.code,
                        'first_name': assignment.operator.person.first_name,
                        'last_name': assignment.operator.person.last_name,
                        'role': assignment.rol,
                        'assigned_at': assignment.assigned_at,
                        'salary': assignment.operator.salary,
                    }
                    operators_data.append(operator_data)
                
                # Combine order, operators, and summary data
                order_with_operators_and_summary = {
                    'order': order_data,
                    'assigned_operators': operators_data,
                    'summary': summary_data
                }
                
                result.append(order_with_operators_and_summary)
            
            return paginator.get_paginated_response(result)
            
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching orders with operators and summary: {str(e)}",
                "messUser": "Error fetching orders with operators and summary",
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
            orders = self.order_service.get_all_orders_report(company_id)

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
        order = get_object_or_404(Order, key=pk)
        
        # Validate if the order is already completed
        if order.status == 'finished':
            return Response(
                {"error": "This order is already finalized. It cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar estado
        valid_statuses = ["pending", "in progress", "finished"]
        status_param = request.data.get("status", "").lower()
        
        if status_param not in valid_statuses:
            return Response(
                {"error": f"Invalid state. Valid states are: {', '.join(valid_statuses)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Solo procesar evidence si se envía
        if 'evidence' in request.FILES:
            evidence_file = request.FILES['evidence']
            
            # Eliminar archivo antiguo
            if order.evidence:
                order.evidence.delete(save=False)
            
            # Procesar la imagen manualmente
            processor = ImageProcessor()
            compressed_image = processor.compress_image(
                evidence_file, 
                quality=75,
                prefix="evidence"
            )
            
            # Generar la ruta usando tu función
            file_path = upload_evidence_file(order, evidence_file.name)
            
            # Asignar el archivo procesado con la ruta correcta
            order.evidence.save(file_path, compressed_image, save=False)
        
        # Actualizar estado
        order.status = status_param
        order.save()

        # Serializar con contexto request
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        # logger.info("=== STARTING ORDER CREATION ===")
        # logger.debug(f"Request headers: {request.headers}")
        # logger.debug(f"Request data: {request.data}")
        print(f"create order: fecha: {request.data}")
        serializer = OrderSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = serializer.save()
            logger.info(f"Order created successfully: {order.key}")
            return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Critical error during order creation: {str(e)}")
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
        Partially updates an order.
        """

        # 3) get an order or 404
        order = get_object_or_404(Order, key=pk)

        # 4) block is finished
        if order.payStatus == 1:
            return Response(
                {"error": "Cannot edit finalized order"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not hasattr(request, 'company_id'):
            request.company_id = order.id_company_id
            logger.debug(f"Forced request.company_id = {request.company_id}")

        serializer = OrderSerializer(
            order,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        try:
            #validate & save
            serializer.is_valid(raise_exception=True)
            updated_order = serializer.save()
            logger.info(f"Order updated successfully: {updated_order.key}")

            # serializer output
            out_data = OrderSerializer(updated_order, context={'request': request}).data
            return Response(out_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            logger.warning(f"Validation errors: {ve.detail}")
            return Response(
                {"error": ve.detail},
                status=status.HTTP_400_BAD_REQUEST
            )

        except PermissionDenied as pd:
            logger.warning(f"Permission denied: {pd}")
            return Response(
                {"error": str(pd)},
                status=status.HTTP_403_FORBIDDEN
            )

        except Exception as e:
            tb = traceback.format_exc()
            print("🔴 TRACEBACK:\n", tb)
            logger.error("❌ Exception in partial_update:\n" + tb)
            return Response(
                {"error": f"{e.__class__.__name__}: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def summary_orders_list(self, request):
        """
        Retrieves a paginated list of orders with a summary of costs.

        Returns:
        - 200 OK: A JSON object with the paginated list of orders and their respective summaries.
        - 400 Bad Request: If an error occurs.
        """
        try:
            company_id = request.company_id
            # Get all orders using the service
            orders = self.order_service.get_all_orders_report(company_id)
            
            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)

            # Prepare the response data
            orders_summary = []
            for order in paginated_orders:
                # Extract the required fields
                customer_name = (
                    order.customer_factory.name if order.customer_factory and order.customer_factory.name else None
                )
                customer_id = (
                    order.customer_factory.id_factory if order.customer_factory and order.customer_factory.id_factory else None
                )

                order_data = {
                    "key": order.key,
                    "key_ref": order.key_ref,
                    "client": order.person.first_name + " " + order.person.last_name,
                    "date": order.date,
                    "state": order.state_usa,
                    "status": order.status,
                    "customer_name": customer_name,
                    "customer_factory_id": customer_id,
                    "payStatus": order.payStatus,
                    "income": order.income
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
            company_id = request.company_id
            # Get all orders using the service
            orders = self.order_service.get_all_pending_orders(company_id)

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

    #just update image
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
    @extend_schema(
        summary="Get all states in USA",
        description="Returns a list of all states in USA.",
        responses={200: StatesUSASerializer(many=True)}
    )
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
    

    def create_workhouse(self, request):
        """
        Create a new workhouse order.
        
        Expected body:
        {
            "date": "2025-05-24",
            "status": "Pending",  # opcional, default: "Pending"
            "person_id": 7,       # requerido
            "customer_factory": 2, # opcional
            "dispatch_ticket": "data:image/jpeg;base64,...", # opcional
            "distance": 100,      # opcional
            "expense": 500.00,    # opcional
            "income": 1000.00,    # opcional
            "weight": 2500        # opcional
        }
        
        Notes:
        - job is automatically set to 'workhouse' job type
        - key_ref is automatically generated as WH-XXXX
        """
        logger.info("=== STARTING WORKHOUSE ORDER CREATION ===")
        logger.debug(f"Request data: {request.data}")
        
        try:
            order = self.order_service.create_workhouse_order(request.data, request)
            serializer = OrderSerializer(order, context={'request': request})
            
            logger.info(f"Workhouse order created successfully: {order.key}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            logger.error(f"Validation error in workhouse order: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception(f"Critical error during workhouse order creation: {str(e)}")
            return Response(
                {"error": f"Error creating workhouse order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @extend_schema(
        summary="List all workhouse orders",
        description="Returns a paginated list of all workhouse orders (identified by job name 'workhouse' or key_ref starting with 'WH-').",
        responses={200: OrderSerializer(many=True)}
    )
    def list_workhouse_orders(self, request):
        """
        List all workhouse orders.
        
        Workhouse orders are identified by:
        - job.name = 'workhouse' OR
        - key_ref starting with 'WH-'
        
        Returns:
        - 200 OK: Paginated list of workhouse orders.
        - 400 Bad Request: If an error occurs.
        """
        try:
            company_id = request.company_id
            
            # Get all workhouse orders using the service
            workhouse_orders = self.order_service.get_all_workhouse_orders(company_id)
            
            # Paginate the queryset
            paginator = PageNumberPagination()
            paginated_orders = paginator.paginate_queryset(workhouse_orders, request)
            
            # Serialize the paginated data
            serialized_orders = OrderSerializer(paginated_orders, many=True, context={'request': request})
            
            return Response({
                "status": "success",
                "messDev": f"Workhouse orders listed successfully. Current company id: {company_id}",
                "messUser": "Workhouse orders listed successfully",
                "current_company_id": company_id,
                "data": paginator.get_paginated_response(serialized_orders.data).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching workhouse orders: {str(e)}")
            return Response({
                "status": "error",
                "messDev": f"Error fetching workhouse orders: {str(e)}",
                "messUser": "Error fetching workhouse orders",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            


    def summary_orders_list_financial(self, request):
        """
        Retrieves a paginated list of orders with a summary of costs, paginated by week.
        """
        try:
            company_id = request.company_id
            number_week = request.query_params.get('number_week')
            year = request.query_params.get('year')
            page_size = request.query_params.get('page_size', 10)

            # Validar y convertir parámetros
            if not year:
                year = datetime.now().year
            else:
                year = int(year)

            if number_week:
                number_week = int(number_week)
                if number_week < 1 or number_week > 53:
                    return Response({
                        "status": "error",
                        "messDev": "Invalid week number.",
                        "messUser": "El número de semana debe estar entre 1 y 53.",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Calcular fechas de la semana ISO
                start_datetime = datetime.strptime(f'{year}-W{number_week}-1', "%G-W%V-%u")
                start_date = start_datetime.date()
                end_date = start_date + timedelta(days=6)
            else:
                start_date = end_date = None

            # Get all orders using the service
            orders = self.order_service.get_all_orders_report(company_id)

            # Filtrar por semana si corresponde
            if start_date and end_date:
                orders = orders.filter(date__range=(start_date, end_date))

            # Paginate the queryset
            paginator = PageNumberPagination()
            paginator.page_size = int(page_size)
            paginated_orders = paginator.paginate_queryset(orders, request)

            # Prepare the response data
            orders_summary = []
            for order in paginated_orders:
                customer_name = (
                    order.customer_factory.name if order.customer_factory and order.customer_factory.name else None
                )
                customer_id = (
                    order.customer_factory.id_factory if order.customer_factory and order.customer_factory.id_factory else None
                )

                order_data = {
                    "key": order.key,
                    "key_ref": order.key_ref,
                    "client": order.person.first_name + " " + order.person.last_name,
                    "date": order.date,
                    "state": order.state_usa,
                    "status": order.status,
                    "customer_name": customer_name,
                    "customer_factory_id": customer_id,
                    "payStatus": order.payStatus,
                    "income": order.income
                }

                # Calculate the summary for the order using the service
                order_data["summary"] = self.order_service.calculate_summary(order.key)
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