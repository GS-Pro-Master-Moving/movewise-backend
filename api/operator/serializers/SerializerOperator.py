from rest_framework import serializers
from api.operator.models.Operator import Operator
from api.person.models.Person import Person

class SerializerOperator(serializers.ModelSerializer):
    # Campos de Person (mapeados a través de la relación)
    first_name = serializers.CharField(source='person.first_name', required=True)
    last_name = serializers.CharField(source='person.last_name', required=True)
    birth_date = serializers.DateField(source='person.birth_date', required=True)
    type_id = serializers.CharField(source='person.type_id', required=True)
    id_number = serializers.IntegerField(source='person.id_number', required=True)
    address = serializers.CharField(source='person.address', required=True)
    phone = serializers.CharField(source='person.phone', required=True)
    email = serializers.EmailField(source='person.email', required=False, allow_null=True)
    id = serializers.IntegerField(source='id_operator', required=True)  # Agregado para incluir el id del operador

    class Meta:
        model = Operator
        fields = [
            # Campos de Operator
            'number_licence', 'code', 'n_children', 'size_t_shift',
            'name_t_shift', 'salary', 'photo', 'status',
            # Campos de Person (mapeados)
            'first_name', 'last_name', 'birth_date', 'type_id',
            'id_number', 'address', 'phone', 'email',
            'id'  # Agregado al conjunto de campos
        ]

    def create(self, validated_data):
        person_data = validated_data.pop('person', {})
        
        person = Person.objects.create(**person_data)
        
        operator = Operator.objects.create(person=person, **validated_data)
        
        return operator

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        person = instance.person
        person_representation = {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'birth_date': person.birth_date.strftime('%Y-%m-%d'),
            'type_id': person.type_id,
            'id_number': person.id_number,
            'address': person.address,
            'phone': person.phone,
            'email': person.email
        }
        
        return {**representation, **person_representation}