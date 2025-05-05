from rest_framework import serializers
from api.order.models.Order import Order
from django.conf import settings

class SerializerOrderEvidence(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['evidence']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.evidence:
            if settings.USE_S3:
                ret['evidence'] = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{instance.evidence.name}"
            else:
                request = self.context.get('request')
                if request:
                    ret['evidence'] = request.build_absolute_uri(instance.evidence.url)
                else:
                    ret['evidence'] = instance.evidence.url
        return ret

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