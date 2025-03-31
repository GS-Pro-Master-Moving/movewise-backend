from rest_framework import serializers
from api.person.models.Person import Person

def PersonSerializer(person: Person) -> dict:
    class meta(serializers.ModelSerializer.Meta):
        model = Person
        fields = "__all__"