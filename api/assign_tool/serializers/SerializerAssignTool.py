from rest_framework import serializers
from api.assign_tool.models.AssignTool import AssignTool
from api.tool.serializers.SerializerTool import ToolSerializer
from api.tool.models.Tool import Tool
from api.order.models.Order import Order

class SerializerAssignToolInput(serializers.Serializer):
    id_order = serializers.UUIDField()

class SerializerAssignTool(serializers.ModelSerializer):
    # fields to read
    tool = ToolSerializer(source='id_tool', read_only=True)
    key = serializers.UUIDField(read_only=True)
    #fields to update and delete
    id_tool = serializers.PrimaryKeyRelatedField(
        queryset=Tool.objects.all(),
        write_only=True
    )
    key = serializers.UUIDField(
        write_only=True
    )

    class Meta:
        model = AssignTool
        fields = [
            'id_assign_tool',
            'tool',
            'date',
            'id_tool',
            'key'
        ]