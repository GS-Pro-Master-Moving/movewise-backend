from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.company.models.Company import Company
from api.company.serializers.companyCreate_serializer import CompanyCreate_serializer
from api.company.serializers.company_serializer import CompanySerializer
from api.user.serializers.UserSerializer import UserSerializer
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]  # Allow any user to access this view
    authentication_classes = [BasicAuthentication, SessionAuthentication]  # Use Basic and Session authentication

    @extend_schema(
        summary="Register user and company",
        description="""
        Registers a user and a company as a single transaction.
        If one fails, the entire operation is rolled back.
        """,
        request=UserSerializer,
        examples=[
            OpenApiExample(
                {
                    "company": {
                        "license_number": "ABC1234567",
                        "name": "McDonals",
                        "address": "4th elm Street",
                        "zip_code": "1234Code"
                    },
                    "user": {
                        "user_name": "stivencshoo",
                        "password": "password123",
                        "person": {
                            "email": "example@example.com",
                            "first_name": "example name",
                            "last_name": "example Garcia",
                            "birth_date": "1995-08-20",
                            "phone": 3101234567,
                            "address": "Example Street 456",
                            "id_number": 180004244,
                            "type_id": "ID Card"
                        }
                    }
                }
            ),
        ]
    )
    def RegisterUserWithCompany(self, request):
        """
        Registers a user and a company as a single transaction.
        If one fails, the entire operation is rolled back.
        """
        try:
            # Start a transaction
            with transaction.atomic():
                # Extract company and user data from the request
                company_data = request.data.get('company')
                user_data = request.data.get('user')

                if not company_data or not user_data:
                    return Response(
                        {"detail": "Both 'company' and 'user' data are required."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Register the company
                company_serializer = CompanyCreate_serializer(data=company_data)
                if company_serializer.is_valid():
                    company = company_serializer.save()
                else:
                    raise ValueError(
                        {"detail": "Invalid company data", "errors": company_serializer.errors}
                    )

                
                # Add company_id to the person data
                if 'person' in user_data:
                    user_data['person']['id_company'] = company.id  # Link the person to the company

                # Register the user and link it to the company
                user_serializer = UserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                else:
                    raise ValueError(
                        {"detail": "Invalid user data", "errors": user_serializer.errors}
                    )

                # If everything is successful, return the created objects
                return Response(
                    {
                        "company": CompanySerializer(company).data,
                        "user": UserSerializer(user).data
                    },
                    status=status.HTTP_201_CREATED
                )

        except ValueError as e:
            # Handle validation errors and rollback the transaction
            return Response(
                e.args[0],  # Pass the error details
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Handle unexpected errors
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    def get_terms_and_conditions(self, request):
        """
        Returns the terms and conditions as an HTML response.
        """
        # Configurar permisos y autenticación para este método
        self.permission_classes = [AllowAny]
        self.authentication_classes = []

        # Ruta del archivo HTML que contiene los términos y condiciones
        html_file_path = "assets/html/terms_and_conditions.html"

        try:
            # Abre el archivo HTML y léelo
            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            # Devuelve el contenido del archivo como respuesta
            return HttpResponse(html_content, content_type="text/html")

        except FileNotFoundError:
            # Maneja el caso en que el archivo no exista
            return Response(
                {"detail": "Terms and conditions file not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Maneja errores inesperados
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    