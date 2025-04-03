from rest_framework import serializers
from api.order.models.Order import Order
from api.person.serializers.PersonCreateFromOrderSerializer import PersonCreateFromOrderSerializer
from api.job.models import Job  

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    - Includes a nested PersonCreateFromOrderSerializer for the `person` field.
    - Validates and creates the associated Person instance before creating the Order.
    """

    person = PersonCreateFromOrderSerializer()

    class Meta:
        model = Order
        fields = ["key_ref", "date", "distance", "expense", "income", "weight", "status", "payStatus", "state_usa", "person", "job"]

    def create(self, validated_data):
        """
        Creates an Order instance with an associated Person.

        - Extracts and validates the `person` data.
        - Saves the Person instance first.
        - Creates and returns the Order instance with the Person reference.
        """
        person_data = validated_data.pop("person")
        person_serializer = PersonCreateFromOrderSerializer(data=person_data)
        
        if person_serializer.is_valid():
            person = person_serializer.save()
        else:
            raise serializers.ValidationError(person_serializer.errors)
        
        order = Order.objects.create(person=person, **validated_data)
        return order  
    
    def update(self, instance, validated_data):
        """
        Updates an existing Order instance.
        """

        # Manejar la actualización de 'person'
        if "person" in validated_data:
            person_data = validated_data.pop("person")
            person_serializer = PersonCreateFromOrderSerializer(instance.person, data=person_data, partial=True)
            if person_serializer.is_valid():
                person_serializer.save()
            else:
                raise serializers.ValidationError(person_serializer.errors)

        # Manejar la actualización de 'job'
        if "job" in validated_data:
            job_id = validated_data.pop("job")
            try:
                instance.job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise serializers.ValidationError({"job": "Job not found"})

        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance