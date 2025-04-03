from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.assign_tool.services.ServicesAssignTool import ServicesAssignTool
from api.assign_tool.serializers.SerializerAssignTool import SerializerAssignTool

class ControllerAssignTool(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            order_id = request.data['id_order']
            print("Tool ID:", tool_id)
            print("Order ID:", order_id)
            result = self.services_assign_tool.assign_tool(tool_id, order_id)
            if result:
                return Response({"success the tool has been assign to the order": result}, status=status.HTTP_200_OK)
            else:
                return Response({"error the order or the tool was not found": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def unassign_tool(self, request):
        """
        Unassign a tool from an order.
        
        Returns:
        - 200 OK: Tool unassigned successfully.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data)
        if serializer.is_valid():
            tool_id = serializer.validated_data['id_tool']
            order_id = serializer.validated_data['id_order']
            result = self.services_assign_tool.unassign_tool(tool_id, order_id)
            if result:
                return Response({"success the tool has been assign to the order": result}, status=status.HTTP_200_OK)
            else:
                return Response({"The assignation was not found": result},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_assigned_tools(self, request):
        """
        Get all tools assigned to an order.
        
        Returns:
        - 200 OK: List of assigned tools.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['id_order']
            print("Order ID:", order_id)
            tools = self.services_assign_tool.get_assigned_tools(order_id)
            return Response(SerializerAssignTool(tools, many=True).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_assigned_tools_by_job(self, request):
        """
        Get all tools assigned to a job.
        
        Returns:
        - 200 OK: List of assigned tools.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data)
        if serializer.is_valid():
            job_id = serializer.validated_data['id_job']
            print("Job ID:", job_id)
            tools = self.services_assign_tool.get_assigned_tools_by_job(job_id)
            return Response(SerializerAssignTool(tools, many=True).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def bulk_create(self, request):
        """
        Create multiple assignments in bulk.
        
        Returns:
        - 201 Created: Assignments created successfully.
        - 400 Bad Request: Invalid input data.
        """
        serializer = SerializerAssignTool(data=request.data, many=True)
        if serializer.is_valid():
            tools = self.services_assign_tool.create_assignments(serializer.validated_data)# To review
            return Response(tools, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)