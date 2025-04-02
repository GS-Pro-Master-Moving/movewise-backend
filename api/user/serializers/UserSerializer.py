from rest_framework import serializers
from api.user import models
from api.person.models import Person
from api.user.models import User 
from api.person.serializers.PersonSerializer import PersonSerializer

class UserSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    class Meta:
        model = User
        fields = ["person", "user_name", "password"] 

    def validate_email(self, value):
        try:
            Person.objects.get(email=value)
        except Person.DoesNotExist:
            raise serializers.ValidationError("email is not register")
        return value
    
    def create(self, validated_data):
        person_data = validated_data.pop("person")
        person = Person.objects.create(**person_data)
        user = User.objects.create(person=person, **validated_data)
        return user
