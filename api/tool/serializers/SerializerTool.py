from rest_framework import serializers
from api.tool.models.Tool import Tool

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'job']  

    def create(self, validated_data):
        company = validated_data.pop('company', None)
        return Tool.objects.create(company=company, **validated_data)