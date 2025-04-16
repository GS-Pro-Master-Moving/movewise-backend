from rest_framework import serializers
from api.workCost.models.WorkCost import WorkCost

class SerializerTruck(serializers.ModelSerializer):
    """
    Serializer for the Truck model.
    """

    class Meta:
        model = WorkCost
        fields = "__all__"
