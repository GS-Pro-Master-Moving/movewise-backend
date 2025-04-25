from rest_framework import serializers
from api.order.models.Order import Order
from api.person.serializers.PersonCreateFromOrderSerializer import PersonCreateFromOrderSerializer
from api.job.models import Job  
from api.company.models.Company import Company

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    - Includes a nested PersonCreateFromOrderSerializer for the `person` field.
    - Validates and creates the associated Person instance before creating the Order.
    """

    person = PersonCreateFromOrderSerializer()

    class Meta:
        model = Order
        fields = ["key", "key_ref", "date", "distance", "expense", "income", "weight", "status", "payStatus", "state_usa", "person", "job"]
        extra_kwargs = {
            'id_company': {'read_only': True}  
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context missing")

        # Get companty instace
        try:
            company = Company.objects.get(pk=request.company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company in token")

        # process person 
        person_data = validated_data.pop("person")
        person_serializer = PersonCreateFromOrderSerializer(
            data=person_data,
            context={'request': request}
        )
        
        if not person_serializer.is_valid():
            raise serializers.ValidationError({"person": person_serializer.errors})
            
        person = person_serializer.save()

        return Order.objects.create(
            id_company=company, #full instance
            person=person,
            **validated_data
        )
    
    def update(self, instance, validated_data):
        """
        Updates an existing Order instance.
        """

        # Handle 'person' update
        if "person" in validated_data:
            person_data = validated_data.pop("person")
            person_serializer = PersonCreateFromOrderSerializer(instance.person, data=person_data, partial=True)
            if person_serializer.is_valid():
                person_serializer.save()
            else:
                raise serializers.ValidationError(person_serializer.errors)

        #handle job update
        if "job" in validated_data:
            job_id = validated_data.pop("job")
            try:
                instance.job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise serializers.ValidationError({"job": "Job not found"})

        #update rest fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance