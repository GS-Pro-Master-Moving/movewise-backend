from rest_framework import serializers
from api.models import User
from drf_extra_fields.fields import Base64ImageField
from api.person.models import Person
from api.person.serializers.PersonSerializer import PersonSerializer
from api.company.models.Company import Company

class UserSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    photo = Base64ImageField(
        required=False,
        allow_null =True,
        use_url=True, #retrieve url instead binary
    )

    class Meta:
        model = User
        fields = ('user_name', 'password', 'person','photo', 'created_at', 'updated_at')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        person_data = validated_data.pop('person')
        # user_name = validated_data.pop('user_name')
        password = validated_data.pop('password')
        photo = validated_data.pop('photo',None)
        # Obtener la instancia de Company desde person_data
        company = person_data.get('id_company')

        if not company:
            raise serializers.ValidationError({'person': {'id_company': 'This field is required.'}})

        # Crear Person con la instancia de Company
        person = Person.objects.create(
            first_name=person_data['first_name'],
            last_name=person_data['last_name'],
            birth_date=person_data.get('birth_date'),
            phone=person_data.get('phone'),
            address=person_data.get('address'),
            id_number=person_data.get('id_number'),
            type_id=person_data.get('type_id'),
            email=person_data.get('email'),
            id_company=company  # Instancia, no ID
        )

        # Crear User con la instancia de Company
        user = User(
            person=person,
            user_name=validated_data['user_name'],
            id_company=company,  # Instancia, no ID
            photo=photo
        )
        user.set_password(password)
        user.save()

        return user