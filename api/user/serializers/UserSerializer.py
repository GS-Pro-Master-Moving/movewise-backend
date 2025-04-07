from rest_framework import serializers
from api.models import User
from api.person.models import Person
from api.person.serializers.PersonSerializer import PersonSerializer

class UserSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    class Meta:
        model = User
        fields = ('user_name', 'password', 'person', 'created_at', 'updated_at')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        try:
            Person.objects.get(email=value)
        except Person.DoesNotExist:
            raise serializers.ValidationError("email is not register")
        return value
    
    def create(self, validated_data):
        person_data = validated_data.pop('person')
        person = Person.objects.create(**person_data)
        
        password = validated_data.pop('password')
        user = User.objects.create_user(person=person, password=password, **validated_data)
        return user
