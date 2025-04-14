from rest_framework import serializers
from api.truck.models.Truck import Truck

class SerializerTruck(serializers.ModelSerializer):
    """
    Serializer for the Truck model.
    """

    class Meta:
        model = Truck
        fields = ["id_truck", "number_truck", "type", "rol", "name", "status", "category"]
