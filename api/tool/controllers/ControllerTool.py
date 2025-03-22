from rest_framework import status, viewsets
from rest_framework.response import Response
from api.tool.services.ServicesTool import ServicesTool
from api.tool.serializers.SerializerTool import ToolSerializer

class ToolController(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_service = ServicesTool() 

    def list(self, request):
        """Obtiene todas las herramientas"""
        tools = self.tool_service.get_all_tools()  
        return Response(ToolSerializer(tools, many=True).data)  
