from rest_framework import status, viewsets, pagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from api.assign.serializers.SerializerAssign import SerializerAssign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from api.assign.services import ServicesAssign  # Importing the module instead of the class
from api.assign.models.Assign import Assign
from django.db import models
from api.assign.serializers.SerializerAssign import BulkAssignSerializer, AssignOperatorSerializer
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from datetime import datetime, timedelta
from django.db.models.functions import ExtractWeek
from api.payment.models.Payment import Payment
from django.utils import timezone
from api.order.services.ServicesOrder import ServicesOrder
from api.order.serializers.OrderSerializer import OrderSerializer
from api.truck.serializers.SerializerTruck import SerializerTruck
class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class ControllerAssign(viewsets.ViewSet):
    """
    Controller for handling assignments between Operators and Orders.

    This viewset provides an endpoint to:
    - Create multiple assignments at once.
    - Create a new assignment.
    - Retrieve an assignment by ID.
    - List assignments by Operator ID or Order ID.
    - List assignaments by orderKey
    - Update the status of an assignment.
    - Delete an assignment.
    - List operators in an order
    """

    def __init__(self, **kwargs):
        """
        Initializes the ControllerAssign instance.

        This constructor initializes the assignment service, which will be used 
        to handle assignment-related business logic.
        """
        super().__init__(**kwargs)
        self.assign_service = ServicesAssign.ServicesAssign()  # Initialize the Assign service
        self.paginator = CustomPagination()
        self.order_service = ServicesOrder()
    
    @extend_schema(
        summary="List orders with assignments and summaries",
        description="Retrieves a paginated list of orders with their operators, vehicles, workhosts, summaryList and summaryCost.",
        responses={
            200: OpenApiResponse(
                description="Orders and assignments retrieved successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "count": 123,
                            "next": "http://.../api/assign/?page=2",
                            "previous": None,
                            "results": [
                                {
                                    "/* Order data with operators, vehicles, workhosts, summaryList, summaryCost */"
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid request parameters",
                examples=[OpenApiExample(
                    "InvalidParameters",
                    value={"status": "error", "messDev": "<error>", "messUser": "Invalid request parameters.", "data": None}
                )]
            ),
            403: OpenApiResponse(
                description="Permission denied",
                examples=[OpenApiExample(
                    "PermissionDenied",
                    value={"status": "error", "messDev": "<error>", "messUser": "You do not have permission to view these assignments.", "data": None}
                )]
            ),
            500: OpenApiResponse(
                description="Server error",
                examples=[OpenApiExample(
                    "ServerError",
                    value={"status": "error", "messDev": "<error>", "messUser": "An unexpected error occurred while retrieving assignments.", "data": None}
                )]
            )
        }
        
    )
    def list(self, request):
        """
        GET /api/assign/
        Returns paginated list of orders with their operators, vehicles,
        workhosts (additional costs), summaryList and summaryCost.
        """
        try:
            # 1. Obtener todas las órdenes
            orders = self.order_service.get_all_orders()

            # 2. Paginar
            paginator = self.paginator
            page = paginator.paginate_queryset(orders, request, view=self)

            resultados = []
            for order in page:
                # Datos base de la orden
                order_data = OrderSerializer(order).data

                # Asignaciones relacionadas
                assigns = (
                    Assign.objects
                          .filter(order=order)
                          .select_related('operator__person', 'truck', 'payment')
                )

                # Operadores asignados (incluye 'role')
                order_data['operators'] = AssignOperatorSerializer(assigns, many=True).data

                # Vehículos asignados sin duplicados
                seen = set()
                vehicles = []
                for a in assigns:
                    t = a.truck
                    if t and t.id_truck not in seen:
                        seen.add(t.id_truck)
                        vehicles.append(SerializerTruck(t).data)
                order_data['vehicles'] = vehicles

                # Workhosts (costos adicionales)
                order_data['workhosts'] = [
                    {'assign_id': a.id, 'cost': a.additional_costs or 0}
                    for a in assigns
                ]

                # SummaryList y SummaryCost
                order_data['summaryList'] = self.order_service.calculate_summary_list(order.key)
                order_data['summaryCost'] = self.order_service.calculate_summary(order.key)

                resultados.append(order_data)

            # 3. Devolver respuesta paginada
            return paginator.get_paginated_response(resultados)

        except ValidationError as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "Invalid request parameters.",
                "data":     None
            }, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "You do not have permission to view these assignments.",
                "data":     None
            }, status=status.HTTP_403_FORBIDDEN)

        except Exception as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "An unexpected error occurred while retrieving assignments.",
                "data":     None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Create multiple assignments",
        description="Creates multiple assignments at once using the provided data.",
        request=SerializerAssign(many=True),
        responses={
            201: OpenApiResponse(
                description="Assignments created successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Assignments created successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Error creating assignments",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={"error": "Failed to create assignments"}
                    )
                ]
            )
        }
    )
    def create_all_assign(self, request):
        """
        Creates multiple assignments at once.

        Delegates the request data to the assignment service. If the operation 
        is successful, it returns a success response; otherwise, it returns an error message.

        Returns:
            - HTTP 201 Created if successful
            - HTTP 400 Bad Request if an error occurs
        """
        success, message = self.assign_service.create_assignments(request.data)  # Use the instance variable

        if success:
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary="Create payment and update multiple assignments",
        description=(
            "Creates a single Payment record and updates multiple Assignments with that payment ID. "
            "If an assignment already has a payment with status 'paid', it will be skipped and reported."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_assigns": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of assignment IDs to update"
                    },
                    "value": {
                        "type": "number",
                        "description": "Payment amount"
                    },
                    "date_payment": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Payment date (optional, defaults to now)"
                    },
                    "bonus": {
                        "type": "number",
                        "description": "Optional bonus amount"
                    },
                    "status": {
                        "type": "string",
                        "description": "Payment status (e.g. 'paid', 'pending')"
                    },
                    "date_start": {
                        "type": "string",
                        "format": "date",
                        "description": "Start date for the payment period"
                    },
                    "date_end": {
                        "type": "string",
                        "format": "date",
                        "description": "End date for the payment period"
                    }
                },
                "required": ["id_assigns", "value", "status", "date_start", "date_end"]
            }
        },
        responses={
            201: OpenApiResponse(
                description="Payment created and assignments updated",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "status": "success",
                            "messDev": "Payment created and assignments updated",
                            "messUser": "Operation successful",
                            "data": {
                                "payment": {
                                    "id_pay": 1,
                                    "value": 10020.00,
                                    "date_payment": "2025-04-25T12:00:00Z",
                                    "bonus": 0.00,
                                    "status": "paid",
                                    "date_start": "2025-04-21",
                                    "date_end": "2025-04-27"
                                },
                                "updated_assigns": [1, 2, 3],
                                "skipped_assigns": [4],
                                "not_found_assigns": []
                            }
                        }
                    )
                ]
            ),
            400: [
                OpenApiResponse(
                    description="Validation error",
                    examples=[
                        OpenApiExample(
                            "Missing Fields",
                            value={
                                "status": "error",
                                "messDev": "Validation errors",
                                "messUser": "Invalid data",
                                "data": {
                                    "id_assigns": ["At least one assignment ID is required"],
                                    "value": ["Value is required"]
                                }
                            }
                        )
                    ]
                ),
                OpenApiResponse(
                    description="All assignments already paid",
                    examples=[
                        OpenApiExample(
                            "Already Paid",
                            value={
                                "status": "error",
                                "messDev": "All assignments are already paid",
                                "messUser": "No assignments were updated because they are already paid",
                                "data": {
                                    "already_paid": [1, 2],
                                    "not_found_assigns": [5]
                                }
                            }
                        )
                    ]
                )
            ],
            404: OpenApiResponse(
                description="No assignments found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={
                            "status": "error",
                            "messDev": "No assignments found with provided IDs",
                            "messUser": "No assignments found for given assignment IDs",
                            "data": {
                                "not_found_assigns": [10, 11, 12]
                            }
                        }
                    )
                ]
            )
        }
    )
    def create_assign_payment(self,request):
        """
        Receives:
        - id_assigns: list of Assign IDs
        - value, date_payment, bonus, status, date_start, date_end

        Creates a single Payment and updates in bulk all Assign records with that payment,
        skipping any assignment that already has a payment in status 'paid'.
        """
        data = request.data

        # 1) Extract and validate fields
        id_assigns = data.get('id_assigns', [])
        value      = data.get('value')
        date_start = data.get('date_start')
        date_end   = data.get('date_end')
        status_p   = data.get('status')
        bonus      = data.get('bonus', 0)
        dp         = data.get('date_payment', None)

        errors = {}
        if not id_assigns:
            errors['id_assigns'] = ['At least one assignment ID is required']
        if value is None:
            errors['value'] = ['Value is required']
        if not status_p:
            errors['status'] = ['Status is required']
        if not date_start:
            errors['date_start'] = ['Start date is required']
        if not date_end:
            errors['date_end'] = ['End date is required']
        if errors:
            return Response({
                'status': 'error',
                'messDev': 'Validation errors',
                'messUser': 'Invalid data',
                'data': errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2) Parse dates
        try:
            date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
            date_end   = datetime.strptime(date_end,   '%Y-%m-%d').date()
            if dp:
                try:
                    dp = datetime.strptime(dp, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    dp = datetime.strptime(dp, '%Y-%m-%d')
            else:
                dp = timezone.now()
        except Exception as e:
            return Response({
                'status': 'error',
                'messDev': f'Invalid date format: {e}',
                'messUser': 'Date format error',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3) Verify assignments exist
        assigns_qs = Assign.objects.filter(id__in=id_assigns)
        found_assigns = list(assigns_qs)
        found_ids = [a.id for a in found_assigns]
        if not found_ids:
            return Response({
                'status': 'error',
                'messDev': 'No assignments found with provided IDs',
                'messUser': 'Invalid assignment IDs',
                'data': {'not_found': id_assigns}
            }, status=status.HTTP_404_NOT_FOUND)

        not_found = [i for i in id_assigns if i not in found_ids]

        # 4) Skip assignments already paid
        already_paid = []
        to_update_ids = []
        for assign in found_assigns:
            if assign.payment and getattr(assign.payment, 'status', '').lower() == 'paid':
                already_paid.append(assign.id)
            else:
                to_update_ids.append(assign.id)

        # If there's nothing to update, return an error
        if not to_update_ids:
            return Response({
                'status': 'error',
                'messDev': 'All assignments are already paid',
                'messUser': 'No assignments were updated because they are already paid',
                'data': {
                    'already_paid': already_paid,
                    'not_found': not_found
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # 5) Create Payment and update Assign in a transaction
        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    value=value,
                    date_payment=dp,
                    bonus=bonus,
                    status=status_p,
                    date_start=date_start,
                    date_end=date_end
                )
                Assign.objects.filter(id__in=to_update_ids).update(payment=payment)

            # 6) Successful response
            return Response({
                'status': 'success',
                'messDev': 'Payment created and assignments updated',
                'messUser': 'Operation successful',
                'data': {
                    'payment': {
                        'id_pay':       payment.id_pay,
                        'value':        float(payment.value),
                        'date_payment': payment.date_payment,
                        'bonus':        float(payment.bonus or 0),
                        'status':       payment.status,
                        'date_start':   payment.date_start,
                        'date_end':     payment.date_end,
                    },
                    'updated_assigns':    to_update_ids,
                    'skipped_assigns':    already_paid,
                    'not_found_assigns':  not_found
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'messDev': f'Error creating payment: {e}',
                'messUser': 'Could not create payment',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="List all assignments with operator details",
        description=(
            "Retrieve all assignments along with operator code, salary, "
            "first and last name, and payment bonus for expense calculation purposes."
        ),
        responses={
            200: OpenApiResponse(
                response=AssignOperatorSerializer(many=True),
                description="A wrapped success response with assignment list"
            ),
            400: OpenApiResponse(description="Bad Request: Invalid parameters or data."),
            401: OpenApiResponse(description="Unauthorized: Missing or invalid credentials."),
            403: OpenApiResponse(description="Forbidden: Insufficient permissions."),
            500: OpenApiResponse(description="Internal Server Error: Unexpected error.")
        }
    )
    def list_assign_operator(self, request):
        """
        GET /api/assign/operators/?number_week=15&year=2025
        Returns paginated assignments filtered by ISO week number and year, with week date range.
        """
        try:
            number_week = request.query_params.get('number_week', None)
            year_param = request.query_params.get('year', None)

            # validate year
            if year_param is not None:
                try:
                    year = int(year_param)
                    if year < 1900 or year > 2100:
                        raise ValueError("Invalid year provided.")
                except ValueError:
                    return Response({
                        "status": "error",
                        "messDev": "Year must be a valid 4-digit number.",
                        "messUser": "The year provided is invalid. Use 4 digits (e.g., 2024).",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                year = datetime.now().year

            start_date = end_date = None
            week_info = {}

            qs = Assign.objects.select_related(
                'operator__person',
                'payment'
            )

            if number_week is not None:
                try:
                    number_week = int(number_week)
                    if number_week < 1 or number_week > 53:
                        raise ValueError("Invalid week number. Must be between 1 and 53.")

                    # Calculate week start date
                    start_date = datetime.strptime(f'{year}-W{number_week}-1', "%G-W%V-%u")
                    end_date = start_date + timedelta(days=6)

                    qs = qs.filter(assigned_at__date__range=(start_date.date(), end_date.date()))

                    week_info = {
                        "week_number": number_week,
                        "year": year,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                    }

                except ValueError as e:
                    return Response({
                        "status": "error",
                        "messDev": str(e),
                        "messUser": "Invalid week number provided.",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            qs = qs.order_by('-assigned_at')

            # Paginate
            page = self.paginator.paginate_queryset(qs, request, view=self)
            serializer = AssignOperatorSerializer(page, many=True)
            data = serializer.data

            if not data:
                return Response({
                    "status":    "success",
                    "messDev":   "No assignments found for the given week.",
                    "messUser":  "There are no assignments for the selected week.",
                    "data":      [],
                    "week_info": week_info or None,
                    "pagination": {
                        "count":     0,
                        "next":      None,
                        "previous":  None,
                        "page_size": self.paginator.page_size,
                    }
                }, status=status.HTTP_200_OK)

            return Response({
                "status":    "success",
                "messDev":   "Assignments retrieved successfully",
                "messUser":  "Assignments list fetched.",
                "data":      data,
                "week_info": week_info or None,
                "pagination": {
                    "count":     self.paginator.page.paginator.count,
                    "next":      self.paginator.get_next_link(),
                    "previous":  self.paginator.get_previous_link(),
                    "page_size": self.paginator.page_size,
                }
            }, status=status.HTTP_200_OK)

        except ValidationError as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "Invalid request parameters.",
                "data":     None
            }, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "You do not have permission to view these assignments.",
                "data":     None
            }, status=status.HTTP_403_FORBIDDEN)

        except Exception as exc:
            return Response({
                "status":   "error",
                "messDev":  str(exc),
                "messUser": "An unexpected error occurred while retrieving assignments.",
                "data":     None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @extend_schema(
        summary="Create a new assignment",
        description="Creates a new assignment between an Operator, a Truck, and an Order.",
        request=SerializerAssign,
        responses={
            201: OpenApiResponse(
                response=SerializerAssign,
                description="Assignment created successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "status": "success",
                            "messDev": "Assignment created successfully",
                            "messUser": "La asignación ha sido creada",
                            "data": {
                                "id": 1,
                                "operator": 1,
                                "order": "ORD123",
                                "truck": 1,
                                "assigned_at": "2025-04-05T10:00:00Z",
                                "rol": "driver"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid data",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "status": "error",
                            "messDev": "Validation error",
                            "messUser": "Datos inválidos",
                            "data": {
                                "operator": ["This field is required."],
                                "order": ["This field is required."],
                                "truck": ["This field is required."]
                            }
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        serializer = SerializerAssign(data=request.data)
        if serializer.is_valid():
            operator_id = serializer.validated_data["operator"].id_operator
            order = serializer.validated_data["order"]
            additional_costs = serializer.validated_data["additional_costs"]
            rol = serializer.validated_data["rol"]  # Obtener el rol
            
            # Get the truck ID (it can be None)
            truck = serializer.validated_data.get("truck")
            truck_id = truck.id_truck if truck else None
            
            # Check if the assignment already exists
            existing_assign = Assign.objects.filter(
                operator__id_operator=operator_id, 
                order__key=order.key, 
                truck__id_truck=truck_id
            ).first()
            
            if existing_assign:
                return Response({
                    "status": "error",
                    "messDev": "Assignment already exists",
                    "messUser": "This assignment already exists",
                    "data": SerializerAssign(existing_assign).data
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get complete objects for validation
            operator = get_object_or_404(Operator, id_operator=operator_id)
            order_obj = get_object_or_404(Order, key=order.key)

            # Create the assignment
            try:
                assign = self.assign_service.create_assign(
                    operator_id=operator.id_operator,
                    truck_id=truck_id,
                    order_id=str(order_obj.key),  # Convert UUID to string if necessary
                    additional_costs=additional_costs,
                    rol=rol  # Pasar el rol a la creación de la asignación
                )
                
                return Response({
                    "status": "success",
                    "messDev": "Assignment created successfully",
                    "messUser": "The assignment has been created",
                    "data": SerializerAssign(assign).data
                }, status=status.HTTP_201_CREATED)
                
            except ValueError as e:
                return Response({
                    "status": "error",
                    "messDev": str(e),
                    "messUser": "Invalid data for the assignment",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "error",
            "messDev": "Validation error",
            "messUser": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Create multiple assignments",
        description="Creates multiple assignments at once using the provided data.",
        request=BulkAssignSerializer(many=True),
        responses={
            201: OpenApiResponse(
                description="Assignments created successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Assignments created successfully"}
                    )
                ]
            )
        }
    )
    def bulk_create(self, request):
        serializers = [SerializerAssign(data=item) for item in request.data]
        
        # Initial validation
        errors = []
        for idx, serializer in enumerate(serializers):
            if not serializer.is_valid():
                errors.append({
                    'index': idx,
                    'errors': serializer.errors,
                    'operator_id': request.data[idx].get('operator'),
                    'message': "Validation error in the operator assignment"
                })
        
        if errors:
            return Response({
                "status": "error",
                "messDev": "Validation errors found",
                "messUser": "Please check the assignment data",
                "data": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                created_assigns = []
                conflicts = []
                
                for idx, serializer in enumerate(serializers):
                    data = serializer.validated_data
                    operator_id = data["operator"].id_operator
                    order = data["order"]
                    truck = data.get("truck")
                    truck_id = truck.id_truck if truck else None

                    # Check for existing assignment
                    existing_assign = Assign.objects.filter(
                        operator__id_operator=operator_id,
                        order__key=order.key
                    )
                    
                    if existing_assign.exists():
                        # Provide detailed information about the conflict
                        existing = existing_assign.first()
                        truck_info = f"with truck {existing.truck.id_truck}" if existing.truck else "without truck"
                        
                        conflicts.append({
                            'index': idx,
                            'operator_id': operator_id,
                            'order_key': str(order.key),
                            'message': f"Operator already assigned to this order {truck_info}"
                        })
                        continue  # Skip this record but continue with the others

                    # Create assignment
                    assign = self.assign_service.create_assign(
                        operator_id=operator_id,
                        truck_id=truck_id,
                        order_id=str(order.key),
                        additional_costs=data.get("additional_costs"),
                        rol=data.get("rol")
                    )
                    created_assigns.append(assign)

                if conflicts:
                    return Response({
                        "status": "partial_success",
                        "messDev": f"Created {len(created_assigns)} assignments, {len(conflicts)} conflicts",
                        "messUser": f"{len(created_assigns)} assignments were saved. {len(conflicts)} operators were already assigned.",
                        "data": {
                            "created": SerializerAssign(created_assigns, many=True).data,
                            "conflicts": conflicts
                        }
                    }, status=status.HTTP_207_MULTI_STATUS)

                return Response({
                    "status": "success",
                    "messDev": f"{len(created_assigns)} assignments created",
                    "messUser": "All assignments completed successfully",
                    "data": SerializerAssign(created_assigns, many=True).data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": str(e),
                "messUser": "Unexpected error during assignments",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @extend_schema(
        summary="Retrieve an assignment",
        description="Retrieves a specific assignment by its ID.",
        responses={
            200: OpenApiResponse(
                response=SerializerAssign,
                description="Assignment retrieved successfully"
            ),
            404: OpenApiResponse(
                description="Assignment not found",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={"error": "Assign not found"}
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """
        Retrieves a specific assignment by its ID.

        If the assignment exists, its details are returned. Otherwise, 
        an error response is provided.

        Returns:
            - HTTP 200 OK with the assignment data if found
            - HTTP 404 Not Found if the assignment does not exist
        """
        assign = self.assign_service.get_assign_by_id(pk)
        if assign:
            return Response(SerializerAssign(assign).data, status=status.HTTP_200_OK)
        return Response({"error": "Assign not found"}, status=status.HTTP_404_NOT_FOUND)


    @extend_schema(
        summary="List assignments by truck",
        description="Retrieves all assignments associated with a specific truck.",
        responses={
            200: OpenApiResponse(
                response=SerializerAssign(many=True),
                description="List of assignments for the specified truck"
            )
        }
    )   

    @extend_schema(
        summary="List assignments by operator",
        description="Retrieves all assignments associated with a specific operator.",
        responses={
            200: OpenApiResponse(
                response=SerializerAssign(many=True),
                description="List of assignments for the specified operator"
            )
        }
    )
    def list_by_operator(self, request, operator_id):
        # First, check if the operator exists
        try:
            operator = Operator.objects.get(id_operator=operator_id)
        except Operator.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Operator not found",
                "messUser": "Operador no encontrado",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # If the operator exists, retrieve their assignments
        assignments = Assign.objects.filter(operator=operator)
        serializer = SerializerAssign(assignments, many=True)
        
        return Response({
            "status": "success",
            "messDev": "Assignments retrieved successfully",
            "messUser": "Asignaciones recuperadas con éxito",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    @extend_schema(
        summary="List assignments by order",
        description="Retrieves all assignments linked to a specific order.",
        responses={
            200: OpenApiResponse(
                response=SerializerAssign(many=True),
                description="List of assignments for the specified order"
            )
        }
    )
    def list_by_order(self, request, order_id):
        try:
            order = Order.objects.get(key=order_id)
        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Order not found",
                "messUser": "Orden no encontrada",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": "Error al recuperar la orden",
                "messUser": f"{str(e)}",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        assignments = Assign.objects.filter(order=order)
        serializer = SerializerAssign(assignments, many=True)
        
        return Response({
            "status": "success",
            "messDev": "Assignments retrieved successfully",
            "messUser": "Asignaciones recuperadas con éxito",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Update an existing assignment",
        description="Updates the details of an existing assignment identified by its ID.",
        request=SerializerAssign,
        responses={
            200: OpenApiResponse(
                response=SerializerAssign,
                description="Assignment updated successfully"
            ),
            400: OpenApiResponse(
                description="Invalid data",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "status": "error",
                            "messDev": "Datos inválidos",
                            "messUser": "Datos inválidos",
                            "data": {
                                "operator": ["Invalid operator ID."]
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Assignment not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={
                            "status": "error",
                            "messDev": "Asignación no encontrada",
                            "messUser": "Asignación no encontrada",
                            "data": None
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """
        Updates an existing assignment.
        """
        serializer = SerializerAssign(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "messDev": "Datos inválidos",
                "messUser": "Datos inválidos",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar si existe la asignación que queremos actualizar
            assign = self.assign_service.get_assign_by_id(pk)
            if not assign:
                return Response({
                    "status": "error",
                    "messDev": "Asignación no encontrada",
                    "messUser": "Asignación no encontrada",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            # Si se proporcionan todos los campos de unicidad, verificar si ya existe otra asignación con esa combinación
            operator_id = serializer.validated_data.get('operator', assign.operator).id_operator
            order_id = serializer.validated_data.get('order', assign.order).key
            truck_id = serializer.validated_data.get('truck', assign.truck).id_truck if serializer.validated_data.get('truck', assign.truck) else None

            # Verificar si existe otra asignación con la misma combinación (excluyendo la actual)
            existing_assign = Assign.objects.filter(
                operator__id_operator=operator_id,
                order__key=order_id,
                truck__id_truck=truck_id
            ).exclude(id=pk).first()

            if existing_assign:
                return Response({
                    "status": "error",
                    "messDev": "La asignación ya existe",
                    "messUser": "Esta combinación de operador, orden y camión ya está en uso.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar la asignación
            updated_assign = self.assign_service.update_assign(pk, serializer.validated_data)
            
            return Response({
                "status": "success",
                "messDev": "Asignación actualizada correctamente",
                "messUser": "Asignación actualizada correctamente",
                "data": SerializerAssign(updated_assign).data
            }, status=status.HTTP_200_OK)
                
        except IntegrityError as e:
            # Manejar la violación de la restricción de unicidad
            return Response({
                "status": "error",
                "messDev": "Datos inválidos",
                "messUser": "Datos inválidos",
                "data": {
                    "non_field_errors": [
                        "Los campos operator, order, truck deben formar un conjunto único."
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Manejar otras excepciones
            return Response({
                "status": "error",
                "messDev": f"Error al actualizar la asignación: {str(e)}",
                "messUser": "Error al actualizar la asignación",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @extend_schema(
        summary="Update assignment status",
        description="Updates the status of an existing assignment.",
        request={"application/json": {"type": "object", "properties": {"new_status": {"type": "string"}}}},
        responses={
            200: OpenApiResponse(
                response=SerializerAssign,
                description="Assignment status updated successfully"
            ),
            400: OpenApiResponse(
                description="Missing status value",
                examples=[
                    OpenApiExample(
                        "Missing Status",
                        value={"error": "new_status is required"}
                    )
                ]
            )
        }
    )
    def update_status(self, request, assign_id):
        """
        Updates the status of an existing assignment.

        The request must contain a `new_status` field. If the update is successful, 
        the modified assignment is returned.

        Returns:
            - HTTP 200 OK if the update is successful
            - HTTP 400 Bad Request if `new_status` is missing
        """
        new_status = request.data.get("new_status")
        if not new_status:
            return Response({"error": "new_status is required"}, status=status.HTTP_400_BAD_REQUEST)

        assign = self.assign_service.update_assign_status(assign_id, new_status)
        return Response(SerializerAssign(assign).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete an assignment",
        description="Permanently deletes an existing assignment.",
        responses={
            204: OpenApiResponse(
                description="Assignment deleted successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Assign deleted"}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Assignment not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Assign not found"}
                    )
                ]
            )
        }
    )
    def delete(self, request, pk=None):
        """
        Deletes an existing assignment.

        Once deleted, the assignment cannot be recovered.

        Returns:
            - HTTP 204 No Content upon successful deletion
            - HTTP 404 Not Found if the assignment does not exist
        """
        # Verificar si la asignación existe antes de intentar eliminarla
        existing_assign = self.assign_service.get_assign_by_id(pk)
        if not existing_assign:
            return Response({"error": "Assign not found"}, status=status.HTTP_404_NOT_FOUND)

        # Si la asignación existe, proceder a eliminarla
        self.assign_service.delete_assign(pk)
        
        # Si la asignación se elimina correctamente, devolver una respuesta 204 No Content
        return Response({"message": "Assign deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="Get assignment audit history",
        description="Retrieves the complete audit history of an assignment.",
        responses={
            200: OpenApiResponse(
                description="Audit history retrieved successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "audit_records": [
                                {
                                    "id": 1,
                                    "old_operator": 1,
                                    "new_operator": 2,
                                    "old_truck": 1,
                                    "new_truck": 1,
                                    "modified_at": "2025-04-05T10:30:00Z"
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Assignment not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Assignment not found"}
                    )
                ]
            )
        }
    )
    def audit_history(self, request, pk=None):
        """
        Retrieves the audit history of an assignment.
        
        Returns:
            - HTTP 200 OK with the audit history if the assignment exists
            - HTTP 404 Not Found if the assignment does not exist
        """
        assign = self.assign_service.get_assign(pk)
        if not assign:
            return Response({
                "status": "error",
                "messDev": "Asignación no encontrada",
                "messUser": "Asignación no encontrada",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the audit records for this assignment
        audit_records = self.assign_service.get_assign_audit_history(pk)
        
        return Response({
            "status": "success",
            "messDev": "Historial de auditoría recuperado correctamente",
            "messUser": "Historial de cambios recuperado correctamente",
            "data": {
                "assign_id": pk,
                "audit_records": audit_records
            }
        }, status=status.HTTP_200_OK)
    

    @extend_schema(
        summary="Get assigned operators for an order",
        description="Returns all operators assigned to a specific order using its key.",
        responses={
            200: SerializerAssign(many=True),
            404: OpenApiResponse(
                description="Order not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Order not found"}
                    )
                ]
            )
        }
    )
    
    def get_assigned_operators(self,order_key):
        """
        Retrieves all operators assigned to a specific order.
        
        This enhanced version uses the inheritance relationship between Operator and Person
        to fetch complete information.

        Args:
            order_key: The key of the order for which assigned operators are desired.

        Returns:
            - HTTP 200 OK with the list of assigned operators if the order exists
            - HTTP 404 Not Found if the order does not exist
        """
        # Check if the order exists
        try:
            order = Order.objects.get(key=order_key)
        except Order.DoesNotExist:
            return Response(
                {"status": "error", "messUser": "Orden no encontrada", "messDev": f"Order with key={order_key} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Query the Assign model to find all assignments related to this order
        # Use select_related to also fetch the related operator information
        # Since Operator inherits from Person, we don't need to explicitly select "person"
        assigned_operators = Assign.objects.filter(order__key=order_key).select_related('operator')
        
        # Prepare the response data with operator and person details
        operator_data = []
        for assignment in assigned_operators:
            operator = assignment.operator
            
            # Since Operator inherits from Person, all Person fields are directly accessible on operator
            operator_info = {
                # Operator-specific fields
                "id": operator.id_operator,
                "number_licence": operator.number_licence,
                "code": operator.code,
                "n_children": operator.n_children,
                "size_t_shift": operator.size_t_shift,
                "name_t_shift": operator.name_t_shift,
                "salary": operator.salary,
                "photo": operator.photo,
                "status": operator.status,
                "assigned_at": assignment.assigned_at,
                "additional_costs": assignment.additional_costs,
                # Getting the operator's role in the assign
                "rol": assignment.rol,
                # Person fields (inherited fields)
                "first_name": operator.first_name if hasattr(operator, 'first_name') else None,
                "last_name": operator.last_name if hasattr(operator, 'last_name') else None,
                "identification": operator.identification if hasattr(operator, 'identification') else None,
                "email": operator.email if hasattr(operator, 'email') else None,
                "phone": operator.phone if hasattr(operator, 'phone') else None,
                "address": operator.address if hasattr(operator, 'address') else None,
            }
            # Optionally include user and company information if needed
            if hasattr(operator, 'user') and operator.user:
                operator_info.update({
                    "username": operator.user.user_name,
                })
                
            if hasattr(operator, 'id_company') and operator.id_company:
                operator_info.update({
                    "company_id": operator.id_company.id,
                    "company_name": operator.id_company.name if hasattr(operator.id_company, 'name') else None,
                    # Add other company fields as needed
                })
                
            operator_data.append(operator_info)
        
        return Response(
            operator_data, 
            status=status.HTTP_200_OK
        )
        