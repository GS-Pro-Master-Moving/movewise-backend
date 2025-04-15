from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status, viewsets
from api.tool.services.ServicesTool import ServicesTool
from api.tool.serializers.SerializerTool import ToolSerializer

class ControllerTool(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_service = ServicesTool()
        self.paginator = PageNumberPagination()  # Add a paginator instance

    def list(self, request):
        """Obtiene todas las herramientas"""
        tools = self.tool_service.get_all_tools()
        paginated_tools = self.paginator.paginate_queryset(tools, request)  # Paginate the queryset
        return self.paginator.get_paginated_response(ToolSerializer(paginated_tools, many=True).data)