from rest_framework import viewsets, status, pagination 
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.operator.serializers.SerializerUpdateOperator import SerializerOperatorUpdate
from api.operator.services.ServiceOperator import ServiceOperator
from api.person.services.ServicesPerson import ServicesPerson
from api.person.serializers.PersonSerializer import PersonSerializer
class CustomPagination(pagination.PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class ControllerOperator(viewsets.ViewSet):
    """
    Controller for managing Operator entities.

    Provides endpoints for:
    - Creating an operator and its person data.
    - Creating an operator.
    - Updating specific fields of an operator.
    - Retrieving an operator by ID.
    - Listing all operators with pagination.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ServiceOperator()
        self.service_person = ServicesPerson()
        self.paginator = CustomPagination()
        
    def list(self, request):
        """List operators with pagination"""
        operators = self.service.get_all_operators()
        paginated_queryset = self.paginator.paginate_queryset(operators, request)
        serializer = SerializerOperator(paginated_queryset, many=True)
        return self.paginator.get_paginated_response(serializer.data)
    
    # TODO!! 
    def create_operator_person(self, request):
        """
        Create a new operator (including inherited person fields).

        Expects:
        - A JSON body with operator details (including person fields).

        Returns:
        - 201 Created: If the operator is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = SerializerOperator(data=request.data)
        if serializer.is_valid():
            operator = serializer.save()# Seems its better to use the save method of the serializer
            return Response(SerializerOperator(operator).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):
        """
        Create a new operator.

        Expects:
        - A JSON body with operator details.

        Returns:
        - 201 Created: If the operator is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = SerializerOperator(data=request.data)
        if serializer.is_valid():
            operator = self.service.create_operator(serializer.validated_data)
            return Response(SerializerOperator(operator).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch_field(self, request, operator_id, field_name):
        """
        Update a specific field of an operator.

        Expects:
        - A JSON body with `new_value`.

        Path Parameters:
        - `operator_id`: The ID of the operator.
        - `field_name`: The name of the field to update.

        Returns:
        - 200 OK: If the field is successfully updated.
        - 400 Bad Request: If the field name is invalid or the request contains invalid data.
        """
        serializer = SerializerOperatorUpdate(data=request.data)
        if serializer.is_valid():
            new_value = serializer.validated_data['new_value']
            update_methods = {
                "name_t_shift": self.service.update_name_t_shift,
                "size_t_shift": self.service.update_size_t_shift,
            }

            if field_name in update_methods:
                update_methods[field_name](operator_id, new_value)
                return Response({ "message": f"{field_name} updated successfully" }, status=status.HTTP_200_OK)
            else:
                return Response({ "error": "Invalid field" }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_operator_id(self, request, operator_id):
        """
        Get a specific operator.

        Path Parameters:
        - `operator_id`: The ID of the operator.

        Returns:
        - 200 OK: If the operator is successfully retrieved.
        - 404 Not Found: If the operator does not exist.
        """
        operator = self.service.get_operator(operator_id)
        if operator:
            return Response(SerializerOperator(operator).data, status=status.HTTP_200_OK)
        return Response({ "error": "Operator not found" }, status=status.HTTP_404_NOT_FOUND)