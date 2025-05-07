from rest_framework import serializers
from api.models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["email", "first_name", "last_name", "birth_date", "phone", "address", "id_number", "type_id", "id_company"]