from rest_framework import serializers
from api.company.models.company import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'license_number', 'name', 'address', 'zip_code', 'created_at']
        read_only_fields = ['created_at'] 