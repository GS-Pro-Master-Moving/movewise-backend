from rest_framework import serializers
from api.company.models.Company import Company

class CompanyCreate_serializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['license_number', 'name', 'address', 'zip_code', 'created_at']
        read_only_fields = ['created_at'] 