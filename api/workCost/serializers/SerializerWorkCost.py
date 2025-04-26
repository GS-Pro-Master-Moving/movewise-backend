from rest_framework import serializers
from api.workCost.models.WorkCost import WorkCost


class WorkCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCost
        fields = ['id_workCost', 'name', 'cost', 'type']

class SerializerTruck(serializers.ModelSerializer):
    """
    Serializer for the Truck model.
    """

    class Meta:
        model = WorkCost
        fields = "__all__"
