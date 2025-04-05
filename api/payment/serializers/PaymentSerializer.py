from rest_framework import serializers
from api.payment.models.Payment import Payment, PaymentAudit

class PaymentAuditSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo PaymentAudit.
    """
    modified_by = serializers.CharField(source='modified_by.username', read_only=True)

    class Meta:
        model = PaymentAudit
        fields = [
            'id', 'payment', 'old_amount', 'new_amount',
            'old_status', 'new_status', 'old_bonus', 'new_bonus',
            'old_date_start', 'new_date_start', 'old_date_end', 'new_date_end',
            'modified_by', 'modified_at'
        ]
        read_only_fields = fields

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Payment.
    """
    audit_records = PaymentAuditSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id_pay', 'value', 'date_payment',
            'bonus', 'status', 'date_start', 'date_end',
            'audit_records'
        ]
        read_only_fields = ['id_pay', 'audit_records']

    def validate_Value(self, value):
        """
        Valida que el monto sea positivo.
        """
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero")
        return value

    def validate_bonus(self, value):
        """
        Valida que el bonus no sea negativo.
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("El bonus no puede ser negativo")
        return value 