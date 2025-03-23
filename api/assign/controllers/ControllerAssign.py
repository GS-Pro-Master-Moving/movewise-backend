from rest_framework import status, viewsets
from rest_framework.response import Response
from api.assign.services.ServicesAssign import ServicesAssign
from api.assign.serializers.SerializerAssign import SerializerAssign

class ControllerAssign(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assign_service = ServicesAssign()

    def create(self, request):
        """Creates a new assignment"""
        serializer = SerializerAssign(data=request.data)
        if serializer.is_valid():
            assign = self.assign_service.create_assign(
                serializer.validated_data["operator"],
                serializer.validated_data["order"]
            )
            return Response(SerializerAssign(assign).data, status=status.HTTP_201_CREATED)
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
