from rest_framework import viewsets, status, pagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiRequest
from django.db import IntegrityError, transaction

from api.operator.models.Operator import Operator
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.operator.serializers.SerializerUpdateOperator import SerializerOperatorUpdate
from api.operator.services.ServiceOperator import ServiceOperator
from api.person.models.Person import Person


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ControllerOperator(viewsets.ViewSet):
    """
    Controller for managing Operator entities.
    """

    #allow get multipar/form-data file and text
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ServiceOperator()
        self.paginator = CustomPagination()

    @extend_schema(
        summary="Get an operator by number_id",
        description="Get an operator by number_id, including person information.",
        responses={200: SerializerOperator, 404: {"error": "Operator not found"}},
    )
    def getOperatorByNumberId(self, request, operator_id):
        try:
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
        operators = self.service.get_all_operators()
        page = self.paginator.paginate_queryset(operators, request)
        serializer = SerializerOperator(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create an operator (with Person, Sons y archivos)",
        description="Crear operador junto a persona, hijos e imágenes. Este endpoint espera `multipart/form-data`.",
        request={
            'multipart/form-data': SerializerOperator
        },
        responses={201: SerializerOperator, 400: {"errors": "Bad request"}},
    )
    def create(self, request):
        serializer = SerializerOperator(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    operator = serializer.save()
                    return Response(
                        SerializerOperator(operator, context={'request': request}).data,
                        status=status.HTTP_201_CREATED
                    )
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #temporaly alias
    def create_operator_person(self, request):
        return self.create(request)
    @extend_schema(
        summary="Patch a single field of an operator",
        description="Actualiza un campo específico (name_t_shift o size_t_shift).",
        parameters=[
            OpenApiParameter("field_name", str, OpenApiParameter.PATH, description="Campo a actualizar"),
        ],
        request=SerializerOperatorUpdate,
        responses={200: {"message": "Updated"}, 400: {"error": "Bad request"}},
    )
    def patch_field(self, request, operator_id, field_name):
        serializer = SerializerOperatorUpdate(data=request.data)
        if serializer.is_valid():
            new_value = serializer.validated_data['new_value']
            update_methods = {
                "name_t_shift": self.service.update_name_t_shift,
                "size_t_shift": self.service.update_size_t_shift,
            }
            if field_name in update_methods:
                update_methods[field_name](operator_id, new_value)
                return Response({"message": f"{field_name} updated successfully"},
                                status=status.HTTP_200_OK)
            return Response({"error": "Invalid field"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get an operator by internal ID",
        description="Get an operator by its internal DB ID (`id_operator`).",
        responses={200: SerializerOperator, 404: {"error": "Operator not found"}},
    )
    def getOperatorById(self, request, operator_id):
        try:
            person = Person.objects.get(id_person=operator_id)
            operator = Operator.objects.get(person=person)
            serializer = SerializerOperator(operator, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Person.DoesNotExist, Operator.DoesNotExist):
            return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)
