# from rest_framework import serializers
# from api.person.models.Person import Person

# def PersonSerializer(person: Person) -> dict:
#     class meta(serializers.ModelSerializer.Meta):
#         model = Person
#         # fields = "__all__"
#         fields = ["email", "name", "last_name", "birth_date", "cell_phone", "address", "id_number", "type_id"]

from rest_framework import serializers
from api.models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["email", "name", "last_name", "birth_date", "cell_phone", "address", "id_number", "type_id"]