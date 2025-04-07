from rest_framework import serializers
from api.models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["email", "first_name", "last_name", "birth_date", "cell_phone", "address", "id_number", "type_id"]