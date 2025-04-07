from rest_framework import serializers
from api.person.models.Person import Person

class PersonCreateFromOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["email", "first_name", "last_name"]  

    def create(self, validated_data):
        person = Person.objects.filter(email=validated_data["email"]).first()
        
        if not person:  # If person doesnt exists then its created
            person = Person.objects.create(
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"]
            )
        
        return person
