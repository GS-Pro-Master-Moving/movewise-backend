from rest_framework import serializers
from api.order.models.Order import Order
from api.person.serializers.PersonCreateFromOrderSerializer import PersonCreateFromOrderSerializer
from api.job.models import Job  
from api.company.models.Company import Company
from django.conf import settings

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    - Includes a nested PersonCreateFromOrderSerializer for the `person` field.
    - Validates and creates the associated Person instance before creating the Order.
    """

    person = PersonCreateFromOrderSerializer()
    evidence = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["key", "key_ref", "date", "distance", "expense", "income", "weight", "status", "payStatus", "evidence", "state_usa", "person", "job"]
        extra_kwargs = {
            'id_company': {'read_only': True},
            'person':     {'read_only': True}, #no nested
        }

    def get_evidence(self, obj):
        if obj.evidence:
            if settings.USE_S3:
                return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{obj.evidence.name}"
            else:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.evidence.url)
                return obj.evidence.url
        return None

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
        # 1. company‐scope guard
        request = self.context.get('request')
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context missing")

        if instance.id_company_id != request.company_id:
            raise serializers.ValidationError("You do not have permission to update this order")

        # 2. job field
        if "job" in validated_data:
            job_id = validated_data.pop("job")
            try:
                instance.job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                raise serializers.ValidationError({"job": "Job not found"})

        # 3. other updatable fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance