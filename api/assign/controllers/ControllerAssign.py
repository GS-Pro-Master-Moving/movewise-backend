from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.assign.services.ServicesAssign import ServicesAssign
from api.assign.serializers.SerializerAssign import SerializerAssign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order

class ControllerAssign(viewsets.ViewSet):
    """
    Controller for handling assignments between Operators and Orders.

    This viewset provides an endpoint to create assignments by linking an operator
    to an order. It verifies the existence of the provided IDs before processing the request.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assign_service = ServicesAssign()  # Initialize the Assign service

    def create(self, request):
        """
        Creates a new assignment between an Operator and an Order.

        - Validates the incoming request data.
        - Ensures the provided Operator and Order exist.
        - Calls the service layer to create the assignment.
        - Returns the created assignment data in the response.

        Expected request payload:
        {
            "operator": 1,
            "order": "26e89b4f0eee4a50896d4781a464c1a1",
            "assigned_at": "2025-03-23T12:00:00Z",
            "status": "pending"
        }
        """

        serializer = SerializerAssign(data=request.data)
        
        if serializer.is_valid():
            operator_id = serializer.validated_data["operator"].id_operator
            order_id = serializer.validated_data["order"].key 
            print("\noperator serializer:", serializer.validated_data["operator"])
            print("\norder serializer:", serializer.validated_data["order"])
            # Ensure the Operator and Order exist before proceeding
            operator = get_object_or_404(Operator, id_operator=operator_id)
            order = get_object_or_404(Order, key=order_id) 
            print("\noperator id:", operator_id)
            print("\norder id:", order_id)
            # Delegate assignment creation to the service layer
            assign = self.assign_service.create_assign(operator.id_operator, order.key)

            return Response(SerializerAssign(assign).data, status=status.HTTP_201_CREATED)

        # Return validation errors if the request is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        """Gets an assignment by ID"""
        assign = self.assign_service.get_assign_by_id(pk)
        if assign:
            return Response(SerializerAssign(assign).data, status=status.HTTP_200_OK)
        return Response({"error": "Assign not found"}, status=status.HTTP_404_NOT_FOUND)

    def list_by_operator(self, request, operator_id):
        """Gets all assignments for a specific operator"""
        assigns = self.assign_service.get_assigns_by_operator(operator_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)

    def list_by_order(self, request, order_id):
        """Gets all assignments for a specific order"""
        assigns = self.assign_service.get_assigns_by_order(order_id)
        return Response(SerializerAssign(assigns, many=True).data, status=status.HTTP_200_OK)

    def update_status(self, request, assign_id):
        """Updates the status of an assignment"""
        new_status = request.data.get("new_status")
        if not new_status:
            return Response({"error": "new_status is required"}, status=status.HTTP_400_BAD_REQUEST)

        assign = self.assign_service.update_assign_status(assign_id, new_status)
        return Response(SerializerAssign(assign).data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Deletes an assignment"""
        self.assign_service.delete_assign(pk)
        return Response({"message": "Assign deleted"}, status=status.HTTP_204_NO_CONTENT)
