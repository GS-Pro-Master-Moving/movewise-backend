from rest_framework import serializers
from api.truck.models.Truck import Truck

class SerializerTruck(serializers.ModelSerializer):
    """
    Serializer for the Truck model.
    """

    class Meta:
        model = Truck
        fields = ["id_truck", "number_truck", "type", "name", "status", "category"]
        extra_kwargs = {
            'id_company': {'read_only': True}
        }
