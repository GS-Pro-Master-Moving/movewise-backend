from rest_framework import serializers
from api.user.models.User import User
from api.person.models.Person import Person
from api.company.models.Company import Company

class UserRegisterSerializer(serializers.Serializer):
    user_name = serializers.CharField()
    password = serializers.CharField()
    person = serializers.DictField()

    def create(self, validated_data):
        person_data = validated_data.pop('person')
        company_id = person_data.get('id_company')
        if company_id:
            try:
                company_instance = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise serializers.ValidationError({"person": {"id_company": "company_not_found"}})
            person_data['id_company'] = company_instance
        # Crea la persona
        person = Person.objects.create(**person_data)
        # Crea el usuario
        user = User.objects.create_user(
            user_name=validated_data['user_name'],
            password=validated_data['password'],
            person=person,
            id_company=person.id_company
        )
        return user