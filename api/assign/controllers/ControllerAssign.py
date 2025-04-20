from rest_framework import status, viewsets
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
from api.assign.serializers.SerializerAssign import BulkAssignSerializer
from django.db import transaction

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
        # Primero, verifica si la orden existe
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
    
    def get_assigned_operators(self, request, order_key):
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
                
                # Person fields (inherited fields)
                "first_name": operator.first_name if hasattr(operator, 'first_name') else None,
                "last_name": operator.last_name if hasattr(operator, 'last_name') else None,
                "identification": operator.identification if hasattr(operator, 'identification') else None,
                "email": operator.email if hasattr(operator, 'email') else None,
                "phone": operator.phone if hasattr(operator, 'phone') else None,
                "address": operator.address if hasattr(operator, 'address') else None,
                
                # You can add more fields as needed
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
        
    def list_operator_by_order(self, request, order_key=None):
        """
        Retrieves a list of operators assigned to a specific order.

        Args:
            order_key: The key of the order for which assigned operators are desired.

        Returns:
            - HTTP 200 OK: A list of operators assigned to the order.
            - HTTP 404 Not Found: If the order does not exist.
        """
        if not order_key:
            return Response({
                "status": "error",
                "messDev": "Missing order_key in URL",
                "messUser": "El identificador de la orden es requerido",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the order exists
            order = Order.objects.get(key=order_key)

            # Query the Assign model to find all assignments related to this order
            assigned_operators = Assign.objects.filter(order=order).select_related('operator')

            # Prepare the response data with operator details
            operator_data = []
            for assignment in assigned_operators:
                operator = assignment.operator

                # Include operator-specific and inherited fields
                operator_info = {
                    "id": operator.id_operator,
                    "first_name": operator.first_name if hasattr(operator, 'first_name') else None,
                    "last_name": operator.last_name if hasattr(operator, 'last_name') else None,
                    "email": operator.email if hasattr(operator, 'email') else None,
                    "phone": operator.phone if hasattr(operator, 'phone') else None,
                    "address": operator.address if hasattr(operator, 'address') else None,
                    "number_licence": operator.number_licence,
                    "salary": operator.salary,
                    "status": operator.status,
                    "assigned_at": assignment.assigned_at,
                    "additional_costs": assignment.additional_costs,
                }

                operator_data.append(operator_info)

            return Response({
                "status": "success",
                "messDev": "Operators retrieved successfully",
                "messUser": "Operadores recuperados con éxito",
                "data": operator_data
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": f"Order with key={order_key} does not exist",
                "messUser": "Orden no encontrada",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Unexpected error: {str(e)}",
                "messUser": "Error inesperado al recuperar los operadores",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)