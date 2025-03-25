from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.truck.services.ServicesTruck import ServicesTruck
from api.truck.serializers.SerializerTruck import SerializerTruck
from api.truck.models.Truck import Truck

class ControllerTruck(viewsets.ViewSet):
    """
    Controller for managing trucks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.truck_service = ServicesTruck()  # Service instance

    def list(self, request):
        """
        Returns a list of available (active) trucks.
        """
        trucks = self.truck_service.get_disponibles()
        serializer = SerializerTruck(trucks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Creates a new truck.
        Expected payload:
        {
            "number_truck": "ABC123",
            "type": "Cargo",
            "rol": "Transport",
            "name": "Big Truck"
        }
        """
        serializer = SerializerTruck(data=request.data)
        if serializer.is_valid():
            truck = self.truck_service.create_truck(**serializer.validated_data)
            return Response(SerializerTruck(truck).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        Activates or deactivates a truck.
        Expected payload:
        {
            "status": true  # true for active, false for inactive
        }
        """
        truck = get_object_or_404(Truck, id_truck=pk)
        status_value = request.data.get("status")

        if status_value is None:
            return Response({"error": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        updated_truck = self.truck_service.update_status(truck.id_truck, status_value)
        return Response(SerializerTruck(updated_truck).data, status=status.HTTP_200_OK)
