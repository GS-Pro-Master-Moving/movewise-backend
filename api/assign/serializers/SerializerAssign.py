from rest_framework import serializers
from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
class SerializerAssign(serializers.ModelSerializer):
    """
    Serializer for Assign model using only IDs.
    """

    operator = serializers.PrimaryKeyRelatedField(queryset=Operator.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all()) 

    class Meta:
        model = Assign
        fields = ["id", "operator", "order", "assigned_at", "rol"]
