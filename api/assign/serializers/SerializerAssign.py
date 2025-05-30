from rest_framework import serializers
from api.assign.models.Assign import Assign, AssignAudit
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.assign.models.Assign import AssignAudit
from api.payment.models.Payment import Payment
from api.person.models.Person import Person
from api.order.services import ServicesOrder
from api.workCost.models.WorkCost import WorkCost
from django.db.models import Sum

class AssignOperatorSerializer(serializers.ModelSerializer):
    id_assign  = serializers.IntegerField(source='id')
    date       = serializers.SerializerMethodField()
    code       = serializers.CharField(source='operator.code')
    salary     = serializers.DecimalField(source='operator.salary', max_digits=10, decimal_places=2, coerce_to_string=False)
    first_name = serializers.CharField(source='operator.person.first_name')
    last_name  = serializers.CharField(source='operator.person.last_name')
    bonus      = serializers.DecimalField(source='payment.bonus', max_digits=10, decimal_places=2, allow_null=True)
    role       = serializers.CharField(source='rol', allow_null=True) 
    
    def get_date(self, obj):
        if obj.assigned_at:
            if hasattr(obj.assigned_at, 'strftime'):
                return obj.assigned_at.strftime('%Y-%m-%d')
            return str(obj.assigned_at)
        return None
    
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
            'role'
        )

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email']  # Solo nombre, apellido y correo

class OrderSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)  

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


#report serializers in assign
class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = ['id_truck', 'number_truck', 'type', 'name']

class AssignSummarySerializer(serializers.ModelSerializer):
    operator      = AssignOperatorSerializer(source='*')
    order         = OrderSerializer(source='order', read_only=True)
    truck         = TruckSerializer(read_only=True)
    workhosts     = serializers.DecimalField(source='additional_costs', max_digits=20, decimal_places=2)
    summaryList   = serializers.SerializerMethodField()
    summaryCost   = serializers.SerializerMethodField()

    class Meta:
        model  = Assign
        fields = [
            'id',
            'operator',
            'order',
            'truck',
            'workhosts',
            'summaryList',
            'summaryCost',
        ]

    def get_summaryList(self, obj):
        """
        Call the method in service that generates the list summary.
        """
        svc = ServicesOrder()
        return svc.calculate_summary_list(obj.order.key)

    def get_summaryCost(self, obj):
        work_cost = WorkCost.objects.filter(id_order=obj.order.id).aggregate(total=Sum('cost'))['total'] or 0
        return {
            "expense": obj.order.expense,
            "rentingCost": obj.order.income,
            "fuelCost": 0,
            "workCost": work_cost,
            "driverSalaries": self.get_driver_salaries(obj),
            "otherSalaries": self.get_other_salaries(obj),
            "totalCost": self.get_total_cost(obj, work_cost),
        }
