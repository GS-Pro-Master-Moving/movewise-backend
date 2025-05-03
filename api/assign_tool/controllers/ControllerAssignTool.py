from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.assign_tool.services.ServicesAssignTool import ServicesAssignTool
from api.assign_tool.serializers.SerializerAssignTool import SerializerAssignTool, SerializerAssignToolInput
from api.order.models.Order import Order
from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class ControllerAssignTool(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paginator = CustomPagination()  
        self.services_assign_tool = ServicesAssignTool()
        
    def assign_tool(self, request):
        """
        Assign a tool to an order.
        
        Returns:
        - 200 OK: Tool assigned successfully.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data)
        if serializer.is_valid():
            tool_id = request.data['id_tool']
            order_id = request.data['key']
            print("Tool ID:", tool_id)
            print("Order ID:", order_id)
            result = self.services_assign_tool.assign_tool(tool_id, order_id)
            print("Result of tool assignation:", result)
            if result:
                return Response({"success the tool has been assign to the order": result}, status=status.HTTP_200_OK)
            else:
                return Response({"error the order or the tool was not found": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def unassign_tool(self, request):
        """
        Unassign a tool from an order.
        
        Body (JSON):
        {
            "id_tool": 5,
            "order_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv"
        }
        """
        serializer = SerializerAssignTool(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tool = serializer.validated_data['id_tool']
        order_id = serializer.validated_data['key'] 
        
        if self.services_assign_tool.unassign_tool(tool.id, order_id):
            return Response({
                "status": "success",
                "message": "Tool unassigned successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Assignment not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def get_assigned_tools(self, request, *args, **kwargs):
        """
        Get all tools assigned to an order (paginado).
        """
        try:
            order_id = self.kwargs.get('key', None)
            if not order_id:
                order_id = request.query_params.get('id_order') or request.data.get('id_order')
            
            if not order_id:
                return Response({"id_order": ["Campo requerido"]}, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.services_assign_tool.get_assigned_tools(order_id)
            page = self.paginator.paginate_queryset(queryset, request)
            
            serializer = SerializerAssignTool(page, many=True)
            
            return self.paginator.get_paginated_response(serializer.data)
        
        except Exception as e:
            print("Error:", str(e))
            return Response({"detail": "Error interno"}, status=500)
    def bulk_create(self, request):
        """
        Create multiple assignments in bulk.
        
        Returns:
        - 201 Created: Assignments created successfully.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data, many=True)
        if serializer.is_valid():
            print("Data to create:", serializer.validated_data)
            tools_assigns = self.services_assign_tool.create_assignments(request.data)
            print("Assign created:", tools_assigns)
            return Response(tools_assigns, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)