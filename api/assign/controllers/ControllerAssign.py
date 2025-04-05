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
            order_id = serializer.validated_data["order"].key
            truck_id = serializer.validated_data["truck"].id_truck

            # Check if an assignment with this combination already exists
            existing_assign = Assign.objects.filter(
                operator__id_operator=operator_id, 
                order__key=order_id, 
                truck__id_truck=truck_id
            ).first()
            
            if existing_assign:
                return Response({
                    "status": "error",
                    "messDev": "Assignment already exists",
                    "messUser": "Esta asignación ya existe",
                    "data": SerializerAssign(existing_assign).data
                }, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with creation if no duplicate exists
            operator = get_object_or_404(Operator, id_operator=operator_id)
            order = get_object_or_404(Order, key=order_id)
            truck = get_object_or_404(Truck, id_truck=truck_id)

            assign = self.assign_service.create_assign(operator.id_operator, truck.id_truck, order.key)

            return Response({
                "status": "success",
                "messDev": "Assignment created successfully",
                "messUser": "La asignación ha sido creada",
                "data": SerializerAssign(assign).data
            }, status=status.HTTP_201_CREATED)

        # Return validation errors if the request is invalid
        return Response({
            "status": "error",
            "messDev": "Validation error",
            "messUser": "Datos inválidos",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
        """
        Retrieves all assignments associated with a specific operator.

        Returns:
            - HTTP 200 OK with a list of assignments
        """
        assigns = self.assign_service.get_assigns_by_operator(operator_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)

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
        """
        Retrieves all assignments linked to a specific order.

        Returns:
            - HTTP 200 OK with a list of assignments
        """
        assigns = self.assign_service.get_assigns_by_order(order_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)
    
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
