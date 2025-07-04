from rest_framework import viewsets, status, pagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import IntegrityError, transaction

from api.operator.models.Operator import Operator
from api.operator.serializers.SerializerOperator import SerializerOperator
from api.operator.serializers.SerializerUpdateOperator import SerializerOperatorUpdate
from api.operator.services.ServiceOperator import ServiceOperator
from api.person.models.Person import Person


from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    invalid_page_message = "Página inválida"

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            # Capturamos el error de página inválida
            return None

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        # Eliminamos la URL next si no hay más resultados
        if not self.get_next_link():
            response.data.pop('next', None)
        if not self.get_previous_link():
            response.data.pop('previous', None)
        return response


class ControllerOperator(viewsets.ViewSet):
    """
    Controller for managing Operator entities.
    """

    # allow get multipar/form-data file and text
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ServiceOperator()
        self.paginator = CustomPagination()

    @extend_schema(
        summary="Get an operator by code operator",
        description="Get an operator by code, including person information.",
        responses={200: SerializerOperator, 404: {"error": "Operator not found"}},
    )
    def getOperatorByCode(self, request, code):
        print(">> buscado código:", code)
        try:
            operator = self.service.get_operator_by_code(code)
            if not operator:
                return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)
                
            serializer = SerializerOperator(operator)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error fetching operator: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @extend_schema(
        summary="Get an operator by number_id",
        description="Get an operator by number_id, including person information.",
        responses={200: SerializerOperator, 404: {"error": "Operator not found"}},
    )
    def getOperatorByNumberId(self, request, document_number):
        try:
            operator = self.service.get_operator_by_number_id(document_number)
            if not operator:
                return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)
                
            serializer = SerializerOperator(operator)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error fetching operator: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="List operators with pagination",
        description="List operators with pagination.",
        responses={200: SerializerOperator(many=True)},
    )
    def list(self, request):
        try:
            company_id = request.company_id  # Obtener el company_id del request
            
            operators = self.service.get_all_operators(company_id)
            page = self.paginator.paginate_queryset(operators, request)
            serializer = SerializerOperator(page, many=True, context={'request': request})
            
            response_data = self.paginator.get_paginated_response(serializer.data).data
            response_data['current_company_id'] = company_id  # Agregamos el company_id en la respuesta

            return Response(response_data)

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching operators: {str(e)}",
                "messUser": "Error fetching operators",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @extend_schema(
    summary="List freelance operators with pagination",
    description="List operators with status='freelance' paginated.",
    responses={200: SerializerOperator(many=True)},
    parameters=[
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Items per page'),
    ]
    )
    def list_freelance_operators(self, request):
        try:
            company_id = request.company_id
            
            if not company_id:
                return Response(
                    {"error": "Company context missing"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            operators = self.service.get_freelance_operators(company_id)
            
            page = self.paginator.paginate_queryset(operators, request)
            
            if not page:
                return Response(
                    {
                        "error": "No existe la página solicitada",
                        "available_pages": self.paginator.page.paginator.num_pages if hasattr(self.paginator, 'page') else 0
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SerializerOperator(page, many=True, context={'request': request})
            
            response_data = self.paginator.get_paginated_response(serializer.data).data
            response_data['current_company_id'] = company_id
            response_data['message'] = "Operadores freelance obtenidos exitosamente"
            
            return Response(response_data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @extend_schema(
        summary="List active and freelance operators with pagination",
        description="List operators with status='active' or 'freelance' paginated.",
        responses={200: SerializerOperator(many=True)},
        parameters=[
            OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
            OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Items per page'),
        ]
    )
    def list_active_and_freelance_operators(self, request):
        try:
            company_id = request.company_id
            
            if not company_id:
                return Response(
                    {"error": "Company context missing"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            operators = self.service.get_active_and_freelance_operators(company_id)
            
            page = self.paginator.paginate_queryset(operators, request)
            
            if not page:
                return Response(
                    {
                        "error": "No existe la página solicitada",
                        "available_pages": self.paginator.page.paginator.num_pages if hasattr(self.paginator, 'page') else 0
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SerializerOperator(page, many=True, context={'request': request})
            
            response_data = self.paginator.get_paginated_response(serializer.data).data
            response_data['current_company_id'] = company_id
            response_data['message'] = "Operadores activos y freelance obtenidos exitosamente"
            
            return Response(response_data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def retrieve_freelance_by_code(self, request):
        try:
            company_id = request.company_id
            code = request.query_params.get('code')
            
            if not code:
                return Response(
                    {"error": "El parámetro 'code' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            operator = self.service.get_freelance_operator_by_code(company_id, code)
            
            if not operator:
                return Response(
                    {"error": "Operador freelance no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = SerializerOperator(operator, context={'request': request})
            
            return Response({
                "data": serializer.data,
                "message": "Operador freelance obtenido con éxito",
                "company_id": company_id
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Loggear error aquí
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                    response_data = {
                        "message": "Operator created successfully",
                        "data": SerializerOperator(operator, context={'request': request}).data,
                        "status": status.HTTP_201_CREATED
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
            except IntegrityError as e:
                error_message = f"Database integrity error: {str(e)}"
                return Response({"message": error_message}, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                error_message = f"Unexpected error: {str(e)}"
                return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        error_message = {
            "message": "Validation error",
            "errors": serializer.errors,
            "status": status.HTTP_400_BAD_REQUEST
        }
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        summary="Create a freelance operator with auto-generated code",
        description="Creates a new freelance operator with an auto-generated code in the format FRL-0001, FRL-0002, etc.",
        request={
            'multipart/form-data': SerializerOperator
        },
        responses={201: SerializerOperator, 400: {"errors": "Bad request"}},
    )
    def create_freelance_person(self, request):
        """
        Crea un nuevo operador freelance con un código generado automáticamente en el formato FRL-0001, FRL-0002, etc.
        No se requiere enviar el campo 'code' en la solicitud.
        """
        # Hacer una copia mutable de request.data
        from django.http import QueryDict
        import json
        
        data = request.data.copy()
        if hasattr(data, '_mutable') and not data._mutable:
            data._mutable = True
        
        # Obtener el ID de la compañía del request
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response({
                "message": "Company context is required",
                "status": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar el código único para el freelancer
        code = self.service.generate_freelance_code(company_id)
        
        # Asegurarse de que el código se envíe en los datos
        data['code'] = code
        
        # Establecer el estado como freelance
        data['status'] = 'freelance'
        
        # Si los datos vienen como JSON, necesitamos asegurarnos de que se procesen correctamente
        if request.content_type == 'application/json':
            # Si es JSON, actualizamos el campo 'code' en los datos validados
            try:
                json_data = json.loads(request.body.decode('utf-8'))
                if isinstance(json_data, dict):
                    json_data['code'] = code
                    json_data['status'] = 'freelance'
                    request._full_data = json_data
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Crear una copia mutable del request con los datos actualizados
        request_copy = request
        request_copy.data._mutable = True
        request_copy.data['code'] = code
        request_copy.data['status'] = 'freelance'
        
        # Llamar al método create original con los datos actualizados
        response = self.create(request_copy)
        
        # Si la creación fue exitosa, actualizar el código en la respuesta
        if response.status_code == status.HTTP_201_CREATED and hasattr(response, 'data'):
            response.data['code'] = code
            
        return response
    
    # temporaly alias
    def create_operator_person(self, request):
        return self.create(request)
    
    @extend_schema(
        summary="Patch operator and person",
        description="Updates whole operator and reemplaza imágenes borrando las anteriores"
    )
    def update_operator_person(self, request, id_operator):
        try:
            # Verificar que el operador exista y esté activo
            operator = self.service.get_operator_by_id(id_operator)
            if not operator:
                return Response({"message": "Operator not found or inactive"}, 
                               status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({"message": f"Error fetching operator: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create a mutable copy of request.data to modify if needed
        data = request.data.copy()
        
        # Handle file uploads separately before serializer processing
        files = request.FILES
        
        # Delete existing files only if they're being replaced
        if 'photo' in files and operator.photo:
            operator.photo.delete(save=False)
        if 'license_front' in files and operator.license_front:
            operator.license_front.delete(save=False)
        if 'license_back' in files and operator.license_back:
            operator.license_back.delete(save=False)

        # Only include the files that were actually uploaded
        file_fields = ['photo', 'license_front', 'license_back']
        for field in file_fields:
            if field not in files:
                # Remove the field from data if it's not being updated
                if field in data:
                    data.pop(field)

        serializer = SerializerOperator(
            operator,
            data=data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    operator = serializer.save()
                    return Response({
                        "message": "Operator updated successfully",
                        "data": SerializerOperator(operator, context={'request': request}).data,
                        "status": status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
            except IntegrityError as e:
                return Response(
                    {"message": f"Database integrity error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"message": f"Unexpected error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response({
            "message": "Validation error",
            "errors": serializer.errors,
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        summary="Patch a single field of an operator",
        description="Updates a specific field (name_t_shift or size_t_shift).",
        parameters=[
            OpenApiParameter("field_name", str, OpenApiParameter.PATH, description="field to update"),
        ],
        request=SerializerOperatorUpdate,
        responses={200: {"message": "Updated"}, 400: {"error": "Bad request"}},
    )
    def patch_field(self, request, operator_id, field_name):
        # Verificar que el operador exista y esté activo
        if not self.service.get_operator_by_id(operator_id):
            return Response({"error": "Operator not found or inactive"}, status=status.HTTP_404_NOT_FOUND)
            
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
    def getOperatorById(self, request, id_person):
        try:
            person = Person.objects.get(id_person=id_person)
            operator = Operator.objects.active().get(person=person)
            serializer = SerializerOperator(operator, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Person.DoesNotExist, Operator.DoesNotExist):
            return Response({"error": "Operator not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        summary="Delete an operator (soft delete)",
        description="Mark an operator as inactive instead of physically deleting it.",
        responses={
            200: {"message": "Operator deleted successfully"},
            404: {"error": "Operator not found"},
            500: {"error": "Internal server error"}
        },
    )
    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        try:
            # Verifica primero si el operador existe y está activo
            operator = self.service.get_operator_by_id(pk)
            if not operator:
                return Response({"error": "Operator not found or already inactive"}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # Realiza el soft delete
            result = self.service.delete_operator(pk)
            if result:
                return Response({"message": "Operator deleted successfully"}, 
                               status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to delete operator"}, 
                               status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"error": f"Error deleting operator: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)