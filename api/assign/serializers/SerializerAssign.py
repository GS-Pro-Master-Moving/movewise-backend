from rest_framework import serializers
from api.assign.models.Assign import Assign
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.assign.models.Assign import AssignAudit

class SerializerAssignAudit(serializers.ModelSerializer):
    """
    Serializer for AssignAudit model.
    """
    class Meta:
        model = AssignAudit
        fields = ['id', 'assign', 'old_operator', 'new_operator', 'old_order', 'new_order', 'old_truck', 'new_truck', 'old_payment', 'new_payment', 'old_assigned_at', 'new_assigned_at', 'old_rol', 'new_rol', 'modified_at']
        read_only_fields = fields

class SerializerAssign(serializers.ModelSerializer):
    """
    Serializer for Assign model using only IDs.
    """
    audit_records = SerializerAssignAudit(many=True, read_only=True)

    operator = serializers.PrimaryKeyRelatedField(queryset=Operator.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all(), allow_null=True, required=False)  # Nueva relación opcional
    payment = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all(), allow_null=True, required=False)  # Nueva relación opcional
    additional_costs = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True, required=False)  # Nueva columna de costos adicionales

    class Meta:
        model = Assign
        fields = ["id", "operator", "order", "truck", "payment", "assigned_at", "rol", "audit_records", "additional_costs"]  # Agregada la columna de costos adicionales
        read_only_fields = ["id", "audit_records"]
