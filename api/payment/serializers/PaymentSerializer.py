from rest_framework import serializers
from api.payment.models.Payment import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Payment.
    """

    class Meta:
        model = Payment
        fields = [
            'id_pay', 'value', 'date_payment',
            'bonus', 'status', 'date_start', 'date_end'
        ]
        read_only_fields = ['id_pay']

    def validate_value(self, value):
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