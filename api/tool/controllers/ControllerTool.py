from jsonschema import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status, viewsets
from api.tool.models.Tool import Tool
from api.tool.services.ServicesTool import ServicesTool
from api.tool.serializers.SerializerTool import ToolSerializer

class ControllerTool(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paginator = PageNumberPagination()  # Add a paginator instance
        self.tool_service = ServicesTool()  # Initialize the service
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
    
    def retrieve(self, request, pk=None):
        """
        Get a tool by ID
        """
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response(
                {"detail": "The company ID was not found in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar la herramienta por ID y compañía
        tool = Tool.objects.filter(id=pk, company_id=company_id, state=True).first()
        if not tool:
            return Response(
                {"detail": "Tool not found or does not belong to the company"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serializar y devolver la herramienta
        serialized_data = ToolSerializer(tool).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create a new tool associated with the company from the token.
        """
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response(
                {"detail": "The company ID was not found in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use the service to create the tool
            tool = self.tool_service.create_tool(request.data, company_id)
            return Response(ToolSerializer(tool).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        "Set status of a tool to inactive"
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response(
                {"detail": "The company ID was not found in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        tool = Tool.objects.filter(id=pk, company_id=company_id).first()
        if not tool:
            return Response(
                {"detail": "Tool not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        tool.state = False
        tool.save()
        return Response(
            {"detail": "Tool deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    
    