from rest_framework import serializers
from api.order.models.Order import Order
from django.conf import settings

class SerializerOrderEvidence(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['evidence']

    def to_representation(self, instance):
        evidence_url = (
            instance.evidence.url 
            if instance.evidence 
            else None
        )
        
        if evidence_url and not settings.USE_S3:
            request = self.context.get('request')
            if request:
                evidence_url = request.build_absolute_uri(evidence_url)
        
        return {'evidence': evidence_url}

    def update(self, instance, validated_data):
        if 'evidence' in validated_data:
            # Delete old file if it exists
            if instance.evidence:
                instance.evidence.delete(save=False)
            
            # Set new file
            instance.evidence = validated_data['evidence']
            
            # Only update the evidence field to prevent other fields from being processed
            instance.save(update_fields=['evidence'])
            
        return instance