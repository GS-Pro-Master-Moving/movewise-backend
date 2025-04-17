from rest_framework import serializers
from api.truck.models.Truck import Truck

class SerializerUpdateTruck(serializers.ModelSerializer):
    """
    Serializer for the Truck model in updating its for ignore number_truck validation.
    """

    class Meta:
        model = Truck
        fields = ["id_truck", "type", "name", "status", "category"]
