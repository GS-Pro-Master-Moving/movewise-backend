from rest_framework import serializers
from api.operator.models.Operator import Operator
from api.person.models.Person import Person

class SerializerOperator(serializers.ModelSerializer):
    # Include inherited fields explicitly
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    address = serializers.CharField()

    class Meta:
        model = Operator
        fields = [
            "first_name", "last_name", "email", "phone", "address",  # Fields from Person
            "number_licence", "code", "n_children", "size_t_shift",  # Fields from Operator
            "name_t_shift", "salary", "photo", "status"
        ]

    def create(self, validated_data):
        # Extract Person fields
        person_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "email": validated_data.pop("email"),
            "phone": validated_data.pop("phone"),
            "address": validated_data.pop("address"),
        }

        # Create the Person instance
        person = Person.objects.create(**person_data)

        # Create the Operator instance linked to the Person
        operator = Operator.objects.create(person_ptr=person, **validated_data)
        return operator