from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from api.order.models.Order import Order
from api.person.serializers.PersonCreateFromOrderSerializer import PersonCreateFromOrderSerializer
from api.job.models import Job
from api.company.models.Company import Company
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
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
    
    person = PersonCreateFromOrderSerializer(required=False)
    evidence = serializers.SerializerMethodField()
    dispatch_ticket = Base64ImageField(
        required=False,
        allow_null=True,
        use_url=True,    # when serializing returns URL instead of binary
    )
    dispatch_ticket_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            "key", "key_ref", "date", "distance", "expense", "income",
            "weight", "status", "payStatus", "evidence", "dispatch_ticket", "dispatch_ticket_url",
            "state_usa", "person", "job", "customer_factory"
        ]

        extra_kwargs = {
            'id_company': {'read_only': True},
        }
    
    def get_evidence(self, obj):
        if not obj.evidence:
            return None
            
        if settings.USE_S3:
            return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{obj.evidence.name}"
        
        request = self.context.get('request')
        return request.build_absolute_uri(obj.evidence.url) if request else obj.evidence.url  
    
    def validate_dispatch_ticket(self, value):
        """
        Additional validation to ensure images are not too large
        """
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError("The image is too large. The maximum size is 5MB.")
                
            # Comprueba el formato
            valid_formats = ['jpeg', 'jpg', 'png']
            img_format = value.name.split('.')[-1].lower()
            if img_format not in valid_formats:
                raise serializers.ValidationError(f"Unsupported format. Use: {', '.join(valid_formats)}")
        
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'company_id'):
            raise serializers.ValidationError("Company context missing")
        
        company = Company.objects.get(pk=request.company_id)
        
        person_data = validated_data.pop("person", None)
        if person_data:
            person_serializer = PersonCreateFromOrderSerializer(
                data=person_data, context={'request': request}
            )
            person_serializer.is_valid(raise_exception=True)
            person = person_serializer.save()
        else:
            raise serializers.ValidationError("Person data is required for creating an order")
        
        return Order.objects.create(
            id_company=company,
            person=person,
            **validated_data
        )
    def get_dispatch_ticket_url(self, obj):
        if not obj.dispatch_ticket:
            return None
            
        request = self.context.get('request')
        return request.build_absolute_uri(obj.dispatch_ticket.url) if request else obj.dispatch_ticket.url  # ¡Y aquí!

    def update(self, instance, validated_data):
        person_data = validated_data.pop('person', None)

        # Check if the dispatch_ticket image is updated
        if 'dispatch_ticket' in validated_data:
            # If there is a previous image, remove it from the file system
            if instance.dispatch_ticket:
                instance.dispatch_ticket.delete(save=False)

        if person_data:
            ps = PersonCreateFromOrderSerializer(
                instance=instance.person,
                data=person_data,
                partial=True,
                context=self.context
            )
            ps.is_valid(raise_exception=True)
            ps.save()

        return super().update(instance, validated_data)


