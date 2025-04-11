from rest_framework import serializers
from api.operator.models.Operator import Operator
from api.person.models.Person import Person

class SerializerOperator(serializers.ModelSerializer):
    # Campos de Person (todos requeridos excepto email)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    type_id = serializers.CharField(required=True)
    id_number = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = Operator
        fields = [
            # Campos de Person
            "first_name", "last_name", "birth_date", "type_id", "id_number",
            "address", "phone", "email",
            # Campos de Operator
            "number_licence", "code", "n_children", "size_t_shift",
            "name_t_shift", "salary", "photo", "status"
        ]

    def create(self, validated_data):
        # Crear Operator directamente (heredará de Person automáticamente)
        operator = Operator.objects.create(**validated_data)
        return operator