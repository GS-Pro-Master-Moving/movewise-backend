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
        "Get tools associated with the token company"
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response(
                {"detail": "The company ID was not found in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tools = self.tool_service.get_all_tools(company_id)
        paginated_tools = self.paginator.paginate_queryset(tools, request)
        serialized_data = ToolSerializer(paginated_tools, many=True).data
        #add id 
        response = self.paginator.get_paginated_response(serialized_data)
        response.data['current_company_id'] = company_id
        return response