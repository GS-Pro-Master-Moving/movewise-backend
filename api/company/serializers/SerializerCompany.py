from rest_framework import serializers
from api.company.models.Company import Company

class SerializerCompany(serializers.ModelSerializer):
    """
    Serializer for the company model.
    """

    class Meta:
        model = Company
        fields = "__all__"  # Serialize all fields of the Company model