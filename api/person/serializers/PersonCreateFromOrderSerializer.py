# api/person/serializers/PersonCreateFromOrderSerializer.py
from rest_framework import serializers
from api.person.models.Person import Person

class PersonCreateFromOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["email", "first_name", "last_name"]

    def create(self, validated_data):
        #get company_id from the request
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context missing")
            
        company_id = getattr(request, 'company_id', None)
        print(f"Creating person for company ID: {company_id}")
        
        if not company_id:
            raise serializers.ValidationError("Company ID not found in request")

        #search person just in the current company
        person = Person.objects.filter(
            email=validated_data["email"],
            id_company=company_id
        ).first()

        if not person:
            person = Person.objects.create(
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                id_company_id=company_id  # inject company_id
            )
            print(f"New person created: {person.id_person}")
        else:
            print(f"Using existing person: {person.id_person}")
        
        return person