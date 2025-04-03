from rest_framework import serializers
from api.assign_tool.models.AssignTool import AssignTool

class SerializerAssignTool(serializers.ModelSerializer):
    class Meta:
        model = AssignTool
        fields = '__all__'