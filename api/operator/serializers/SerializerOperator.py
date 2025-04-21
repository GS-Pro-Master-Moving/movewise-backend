from rest_framework import serializers
from api.operator.models.Operator import Operator
from api.person.models.Person import Person
from api.son.models.Son import Son

class SonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Son
        fields = ['name', 'birth_date', 'gender']
    
class SerializerOperator(serializers.ModelSerializer):
    # Person fields (mapped)
    first_name = serializers.CharField(source='person.first_name', required=True)
    last_name = serializers.CharField(source='person.last_name', required=True)
    birth_date = serializers.DateField(source='person.birth_date', required=True)
    type_id = serializers.CharField(source='person.type_id', required=True)
    id_number = serializers.IntegerField(source='person.id_number', required=True)
    address = serializers.CharField(source='person.address', required=True)
    phone = serializers.CharField(source='person.phone', required=True)
    email = serializers.EmailField(source='person.email', required=False, allow_null=True)

    # Nested sons
    sons = SonSerializer(many=True, required=False)

    class Meta:
        model = Operator
        fields = [
            'id_operator', 
            'number_licence', 'code', 'n_children', 'size_t_shift',
            'name_t_shift', 'salary', 'photo', 'status',
            # Person fields
            'first_name', 'last_name', 'birth_date', 'type_id',
            'id_number', 'address', 'phone', 'email',
            # Sons
            'sons',
        ]

    def create(self, validated_data):
        person_data = validated_data.pop('person')
        sons_data = validated_data.pop('sons', [])
        
        from django.db import transaction
        with transaction.atomic():
            person = Person.objects.create(**person_data)
            
            operator = Operator.objects.create(person=person, **validated_data)
            
            for son_data in sons_data:
                Son.objects.create(operator=operator, **son_data)
            
            return operator
        
    def update(self, instance, validated_data):
        # Actualizar objeto Person
        person_data = validated_data.pop('person', {})
        person = instance.person
        
        for attr, value in person_data.items():
            setattr(person, attr, value)
        person.save()
        
        # Update children if they exist
        sons_data = validated_data.pop('sons', [])
        if sons_data:
            instance.sons.all().delete()
            for son_data in sons_data:
                Son.objects.create(operator=instance, **son_data)
        
        # Actualizar campos de Operator
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
    