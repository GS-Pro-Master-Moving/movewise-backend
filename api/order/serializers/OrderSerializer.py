from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from api.order.models.Order import Order
from api.person.serializers.PersonCreateFromOrderSerializer import PersonCreateFromOrderSerializer
from api.job.models import Job
from api.company.models.Company import Company
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import uuid
import os

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
     
    - Nested PersonCreateFromOrderSerializer en `person`.
    - Recibe dispatch_ticket en Base64 dentro del JSON.
    - Devuelve evidence y dispatch_ticket como URLs (local o S3).
    """
    
    person = PersonCreateFromOrderSerializer()
    evidence = serializers.SerializerMethodField()
    dispatch_ticket = Base64ImageField(
        required=False,
        allow_null=True,
        use_url=True,    # when serializing returns URL instead of binary
    )
    
    class Meta:
        model = Order
        fields = [
            "key", "key_ref", "date", "distance", "expense", "income",
            "weight", "status", "payStatus", "evidence", "dispatch_ticket",
            "state_usa", "person", "job"
        ]
        extra_kwargs = {
            'id_company': {'read_only': True},
            'person':     {'read_only': True},
        }
    
    def get_evidence(self, obj):
        if not obj.evidence:
            return None
        if settings.USE_S3:
            return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{obj.evidence.name}"
        request = self.context.get('request')
        return request.build_absolute_uri(obj.evidence.url)
    
    def validate_dispatch_ticket(self, value):
        """
        Validación adicional para asegurar que las imágenes no sean demasiado grandes
        """
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError("La imagen es demasiado grande. El tamaño máximo es 5MB.")
                
            # Comprueba el formato
            valid_formats = ['jpeg', 'jpg', 'png']
            img_format = value.name.split('.')[-1].lower()
            if img_format not in valid_formats:
                raise serializers.ValidationError(f"Formato no soportado. Use: {', '.join(valid_formats)}")
        
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context missing")
        
        company = Company.objects.get(pk=request.company_id)
        
        person_data = validated_data.pop("person")
        person_serializer = PersonCreateFromOrderSerializer(
            data=person_data, context={'request': request}
        )
        person_serializer.is_valid(raise_exception=True)
        person = person_serializer.save()
        
        return Order.objects.create(
            id_company=company,
            person=person,
            **validated_data
        )
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context missing")
        if instance.id_company_id != request.company_id:
            raise serializers.ValidationError("You do not have permission to update this order")

        if "job" in validated_data:
            job_id = validated_data.pop("job")
            instance.job = get_object_or_404(Job, id=job_id)

        if "dispatch_ticket" in validated_data:
            if instance.dispatch_ticket:
                old_image_path = instance.dispatch_ticket.path
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
            instance.dispatch_ticket = validated_data.pop("dispatch_ticket")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
