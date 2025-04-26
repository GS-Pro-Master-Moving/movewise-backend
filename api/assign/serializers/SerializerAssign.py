from rest_framework import serializers
from api.assign.models.Assign import Assign, AssignAudit
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.assign.models.Assign import AssignAudit
from api.payment.models.Payment import Payment
from api.person.models.Person import Person

class AssignOperatorSerializer(serializers.ModelSerializer):
    id_assign  = serializers.IntegerField(source='id')
    date       = serializers.DateTimeField(source='assigned_at')
    code       = serializers.CharField(source='operator.code')
    salary     = serializers.DecimalField(source='operator.salary', max_digits=10, decimal_places=2,coerce_to_string=False)
    first_name = serializers.CharField(source='operator.person.first_name')
    last_name  = serializers.CharField(source='operator.person.last_name')
    bonus      = serializers.DecimalField(source='payment.bonus', max_digits=10, decimal_places=2, allow_null=True)

    class Meta:
        model  = Assign
        fields = (
            'id_assign',
            'date',
            'code',
            'salary',
            'first_name',
            'last_name',
            'bonus',
        )

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email']  # Solo nombre, apellido y correo

class OrderSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)  # Incluir el serializer de persona

    class Meta:
        model = Order
        fields = ['key', 'key_ref', 'date', 'distance', 'expense', 'income', 'weight', 'status', 'payStatus', 'evidence', 'state_usa', 'id_company', 'person', 'job', 'assign', 'tool']  # Incluir todos los campos necesarios

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
    Serializer for Assign model with expanded Order.
    """
    audit_records = SerializerAssignAudit(many=True, read_only=True)
    operator = serializers.PrimaryKeyRelatedField(queryset=Operator.objects.all())
    
    # Mantenemos el campo 'order' para uso interno pero sobreescribimos la representación
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    # Añadimos un campo data_order que expande los detalles de la orden
    data_order = OrderSerializer(source='order', read_only=True)
    
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all(), allow_null=True, required=False)
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all(), allow_null=True, required=False)
    additional_costs = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True, required=False)

    class Meta:
        model = Assign
        fields = ["id", "operator", "order", "data_order", "truck", "payment", "assigned_at", "rol", "audit_records", "additional_costs"]
        read_only_fields = ["id", "audit_records", "data_order"]

class BulkAssignSerializer(serializers.Serializer):
    operators = serializers.PrimaryKeyRelatedField(
        queryset=Operator.objects.all(),
        many=True
    )
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    truck = serializers.PrimaryKeyRelatedField(
        queryset=Truck.objects.all(), 
        allow_null=True, 
        required=False
    )
    additional_costs = serializers.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        allow_null=True, 
        required=False
    )
    assigned_at = serializers.DateTimeField()
    rol = serializers.CharField()