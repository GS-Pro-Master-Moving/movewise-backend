from rest_framework import serializers
from api.tool.models.Tool import Tool

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'job']  
