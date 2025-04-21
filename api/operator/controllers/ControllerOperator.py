from rest_framework import viewsets, status, pagination 
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.operator.serializers.SerializerUpdateOperator import SerializerOperatorUpdate
from api.operator.services.ServiceOperator import ServiceOperator
from api.person.services.ServicesPerson import ServicesPerson
from api.person.serializers.PersonSerializer import PersonSerializer
from api.operator.models.Operator import Operator 
from api.person.models.Person import Person
from django.db import IntegrityError
from django.db import transaction

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


    @extend_schema(
        summary="Get an operator by number_id",
        description="Get an operator by number_id, including person information.",
        responses={200: SerializerOperator, 404: {"error": "Operator not found"}},
    )
 
    def getOperatorByNumberId(self, request, operator_id):
        try:
            # Buscar por id_number en Person
            person = Person.objects.get(id_number=operator_id)
            operator = Operator.objects.get(person=person)
            
            serializer = SerializerOperator(operator)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (Person.DoesNotExist, Operator.DoesNotExist):
            return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)
   
    @extend_schema(
        summary="List operators with pagination",
        description="List operators with pagination.",
        responses={200: SerializerOperator(many=True)},
    )
    def list(self, request):
        """List operators with pagination"""
        operators = self.service.get_all_operators()
        paginated_queryset = self.paginator.paginate_queryset(operators, request)
        serializer = SerializerOperator(paginated_queryset, many=True)
        return self.paginator.get_paginated_response(serializer.data)
    

    def create_operator_person(self, request):
        serializer = SerializerOperator(data=request.data)
        if serializer.is_valid():
            try:
                # using atomic to ensure that everything is saved correctly or nothing is saved
                with transaction.atomic():
                    operator = serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Catch other types of exceptions
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        return self.create_operator_person(request)
    

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
    
    def getOperatorById(self, request, operator_id):
        try:
            person = Person.objects.get(id_person=operator_id)
            operator = Operator.objects.get(person=person)
            serializer = SerializerOperator(operator)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Person.DoesNotExist, Operator.DoesNotExist):
            return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)