from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.assign.services.ServicesAssign import ServicesAssign
from api.assign.serializers.SerializerAssign import SerializerAssign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
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
        self.assign_service = ServicesAssign()  # Initialize the Assign service
        
    def create_all_assign(self, request):
        """
        Creates multiple assignments at once.

        Delegates the request data to the assignment service. If the operation 
        is successful, it returns a success response; otherwise, it returns an error message.

        Returns:
            - HTTP 201 Created if successful
            - HTTP 400 Bad Request if an error occurs
        """
        success, message = ServicesAssign.create_assign(request.data)

        if success:
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):
        """
        Creates a new assignment between an Operator, a Truck, and an Order.

        The request must contain the following fields:
        - `operator`: The ID of the operator
        - `truck`: The ID of the truck
        - `order`: The unique key of the order
        - `assigned_at`: The assignment timestamp
        - `rol`: The role of the operator in the assignment

        If the provided IDs exist, the assignment is created and stored.

        Returns:
            - HTTP 201 Created if successful
            - HTTP 400 Bad Request if validation fails
        """
        serializer = SerializerAssign(data=request.data)
        if serializer.is_valid():
            operator_id = serializer.validated_data["operator"].id_operator
            order_id = serializer.validated_data["order"].key
            truck_id = serializer.validated_data["truck"].id_truck

            # Ensure that the Operator, Truck, and Order exist before proceeding
            operator = get_object_or_404(Operator, id_operator=operator_id)
            order = get_object_or_404(Order, key=order_id)
            truck = get_object_or_404(Truck, id_truck=truck_id)

            # Delegate assignment creation to the service layer
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

    def list_by_operator(self, request, operator_id):
        """
        Retrieves all assignments associated with a specific operator.

        Returns:
            - HTTP 200 OK with a list of assignments
        """
        assigns = self.assign_service.get_assigns_by_operator(operator_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)

    def list_by_order(self, request, order_id):
        """
        Retrieves all assignments linked to a specific order.

        Returns:
            - HTTP 200 OK with a list of assignments
        """
        assigns = self.assign_service.get_assigns_by_order(order_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)

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

    def delete(self, request, pk=None):
        """
        Deletes an existing assignment.

        Once deleted, the assignment cannot be recovered.

        Returns:
            - HTTP 204 No Content upon successful deletion
        """

        if not self.assign_service.delete_assign(pk):
            return Response({"error": "Assign not found"}, status=status.HTTP_404_NOT_FOUND)
        # If the assignment is successfully deleted, return a 204 No Content response
        return Response({"message": "Assign deleted"}, status=status.HTTP_204_NO_CONTENT)

