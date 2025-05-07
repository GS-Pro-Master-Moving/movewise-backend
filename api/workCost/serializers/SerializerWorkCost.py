from rest_framework import serializers
from api.workCost.models.WorkCost import WorkCost
from api.order.models.Order import Order
from api.order.serializers.OrderSerializer import OrderSerializer # use orderserializer

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

class WorkCostWithOrderInfoSerializer(serializers.ModelSerializer):
    order = OrderSerializer(source="id_order", read_only=True)

    class Meta:
        model = WorkCost
        fields = "__all__"

