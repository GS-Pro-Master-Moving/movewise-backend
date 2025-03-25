from rest_framework import serializers
from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck

class SerializerAssign(serializers.ModelSerializer):
    """
    Serializer for Assign model using only IDs.
    """

    operator = serializers.PrimaryKeyRelatedField(queryset=Operator.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all(), allow_null=True, required=False)  # Nueva relación opcional

    class Meta:
        model = Assign
        fields = ["id", "operator", "order", "truck", "assigned_at", "rol"]
