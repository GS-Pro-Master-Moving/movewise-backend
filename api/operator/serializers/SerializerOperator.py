import json
from rest_framework import serializers
from api.operator.models.Operator import Operator
from api.person.models.Person import Person
from api.son.models.Son import Son
from django.db import transaction
from django.db import models
from api.company.models.Company import Company

class SonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Son
        fields = ['name', 'birth_date', 'gender']

class SonsField(serializers.ListField):
    child = SonSerializer()

    def to_internal_value(self, data):
        print("🟡 SonsField - Received value:", data)

        # If it arrives as a list with a single string (e.g. ['[{"name":...}]'])
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], str):
            try:
                data = json.loads(data[0])
                print("🟢 SonsField - Parsed JSON from list string:", data)
            except json.JSONDecodeError as e:
                print("🔴 Error parsing JSON from list:", e)
                raise serializers.ValidationError("The 'sons' field must contain valid JSON.")

        elif isinstance(data, str):
            try:
                data = json.loads(data)
                print("🟢 SonsField - Parsed JSON from string:", data)
            except json.JSONDecodeError as e:
                print("🔴 Error parsing JSON from string:", e)
                raise serializers.ValidationError("The 'sons' field must contain valid JSON.")

        if not isinstance(data, list):
            raise serializers.ValidationError("The 'sons' field must be a list.")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Each child must be a JSON object. Error at index {idx}.")

        return super().to_internal_value(data)

    def to_representation(self, value):
        """
        Convierte el RelatedManager a una lista de objetos serializados
        """
        if isinstance(value, models.Manager):
            return super().to_representation(value.all())
        return super().to_representation(value)

class SerializerOperator(serializers.ModelSerializer):
    # Campos embebidos de Person
    first_name   = serializers.CharField(source='person.first_name',  required=True)
    last_name    = serializers.CharField(source='person.last_name',   required=True)
    birth_date   = serializers.DateField(source='person.birth_date',  required=False)
    type_id      = serializers.CharField(source='person.type_id',     required=True)
    id_number    = serializers.CharField(source='person.id_number', required=True)
    address      = serializers.CharField(source='person.address',     required=False)
    phone        = serializers.CharField(source='person.phone',       required=False)
    email        = serializers.EmailField(source='person.email',      required=False, allow_null=True)
    id_company = serializers.IntegerField(
        source='person.id_company_id',
        read_only=True
    )
    # Sons field
    sons = SonsField(
        required=False,
        allow_null=True,  # Add this to handle null values
        help_text="List of children of the operator"
    )

    class Meta:
        model = Operator
        fields = [
            'id_operator',
            'number_licence', 'code', 'n_children', 'size_t_shift',
            'name_t_shift', 'salary',
            'photo', 'license_front', 'license_back', 
            'status',
            # Person fields
            'first_name', 'last_name', 'birth_date', 'type_id',
            'id_number', 'address', 'phone', 'email', 
            'id_company',
            # Children
            'sons',
        ]
        read_only_fields = ['id_company']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context (company_id) missing")

        # 1) Lookup the Company instance
        try:
            company = Company.objects.get(pk=request.company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company in token")

        # 2) Pop and enrich person_data
        person_data = validated_data.pop('person')
        person_data['id_company'] = company

        # 3) Pop sons if any
        sons_data = validated_data.pop('sons', [])

        # 4) Create Person + Operator + Sons in a transaction
        with transaction.atomic():
            person = Person.objects.create(**person_data)
            operator = Operator.objects.create(person=person, **validated_data)

            for son in sons_data:
                # your existing logic for creating each Son…
                if isinstance(son, dict):
                    Son.objects.create(operator=operator, **son)
                else:
                    # if string, parse JSON, etc.
                    try:
                        son_dict = json.loads(son)
                        Son.objects.create(operator=operator, **son_dict)
                    except Exception:
                        # or skip / raise
                        pass

            return operator

    def update(self, instance, validated_data):
        person_data = validated_data.pop('person', {})
        for attr, val in person_data.items():
            setattr(instance.person, attr, val)
        instance.person.save()

        sons_data = validated_data.pop('sons', [])
        if sons_data:
            instance.sons.all().delete()  # delete the existing children
            for son in sons_data:
                Son.objects.create(operator=instance, **son)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
