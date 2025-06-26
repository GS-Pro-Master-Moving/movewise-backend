from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.company.serializers.company_serializer import CompanySerializer
from api.company.services.ServicesCompany import ServicesCompany
from api.person.serializers.PersonSerializer import PersonSerializer
from django.db.models import Q

from api.user.serializers.UserRegisterSerializer import UserRegisterSerializer
from api.user.serializers.UserSerializer import UserSerializer
from api.user.serializers.LoginSerializer import LoginSerializer
from api.user.serializers.LoginResponseSerializer import LoginResponseSerializer
from api.user.services.ServicesUser import ServicesUser
from api.user.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from api.person.models.Person import Person

class UserRegister(APIView):
    permission_classes = [AllowAny]  
    authentication_classes = []
    @extend_schema(
        summary="Register new user and person",
        description="Creates a new user linked to a person in the database.",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: {"example": {"error": "Invalid data"}}
        },
        examples=[
            OpenApiExample(
                "Request example",
                value={
                    "user_name": "maria_garcia",
                    "password": "password123",
                    "person": {
                        "email": "maria@example.com",
                        "name": "Maria",
                        "last_name": "Garcia",
                        "birth_date": "1995-08-20",
                        "cell_phone": 3101234567,
                        "address": "Example Street 456",
                        "id_number": 1122334455,
                        "type_id": "ID Card"
                    }
                },
                request_only=True  # Only for request example
            ),
            OpenApiExample(
                "Successful response example",
                value={
                    "user_name": "maria_garcia",
                    "person": {
                        "email": "maria@example.com",
                        "name": "Maria",
                        "last_name": "Garcia"
                    }
                },
                response_only=True  # Only for response example
            )
        ]
    )
    def post(self, request):
        print("Datos recibidos para registrar usuario:", request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                person_data = serializer.validated_data.get('person')
                email = person_data.get('email')
                id_number = person_data.get('id_number')

                # Buscar persona existente por email o id_number
                person = None
                if email or id_number:
                    person = Person.all_objects.filter(
                        Q(email=email) | Q(id_number=id_number)
                    ).first()

                # Si el nombre de usuario ya existe muestra mensaje de error
                if serializer.validated_data.get('user_name'):
                    from api.user.models.User import User
                    if User.all_objects.filter(user_name=serializer.validated_data.get('user_name')).exists():
                        print("El nombre de usuario ya existe.")
                        return Response(
                            {
                                "messUser": "username_already_exists",
                                "messDev": "Username already exists.",
                                "data": None
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                # Si el email ya esta registrado como usuario muestra mensaje de error
                if email:
                    from api.user.models.User import User
                    if User.all_objects.filter(person__email=email).exists():
                        print("El email ya está registrado.")
                        return Response(
                            {
                                "messUser": "email_already_registered_for_user",
                                "messDev": "Email already registered.",
                                "data": None
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                # Si el id_number ya esta registrado para algun usuario muestra mensaje de error
                if id_number:
                    from api.user.models.User import User
                    if User.all_objects.filter(person__id_number=id_number).exists():
                        print("El número de identificación ya está registrado.")
                        return Response(
                            {
                                "messUser": "id_number_already_registered_for_user",
                                "messDev": "ID number already registered.",
                                "data": None
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                if person:
                    # Si ya existe, crear solo el usuario asociado
                    user_name = serializer.validated_data.get('user_name')
                    password = serializer.validated_data.get('password')
                    id_company = person.id_company

                    # Verifica que no exista ya un usuario para esa persona
                    from api.user.models.User import User
                    if User.all_objects.filter(person=person).exists():
                        print("Ya existe un usuario para esta persona.")
                        return Response(
                            {
                                "messUser": "user_already_exists",
                                "messDev": "A user already exists for this person.",
                                "data": None
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    user = User.objects.create_user(
                        user_name=user_name,
                        password=password,
                        person=person,
                        id_company=id_company
                    )
                    print("Usuario creado para persona existente.")
                    response_data = {
                        "messUser": "user_created_for_existing_person",
                        "messDev": "User created for existing person.",
                        "data": UserSerializer(user).data
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    # Si no existe la persona, crea normalmente (usando el serializer)
                    user = serializer.save()
                    print("Usuario añadido con nueva persona.")
                    response_data = {
                        "messUser": "registration_successful",
                        "messDev": "User registered successfully.",
                        "data": UserSerializer(user).data
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print("Exception: ", str(e))
                return Response(
                    {
                        "messUser": "registration_error",
                        "messDev": str(e),
                        "data": None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        if(serializer.errors):
            print("Errores de validación:", serializer.errors)
        return Response(
            {
                "messUser": "invalid_data",
                "messDev": serializer.errors,
                "data": None
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
class UserLogin(APIView):
    permission_classes = [AllowAny] 
    authentication_classes = []

    @extend_schema(
        summary="Autenticar usuario",
        description="""
        Endpoint para autenticación de usuarios con dos métodos:
        
        1. Administradores (rol=1):
           - Deben autenticarse usando email y password
           - Ejemplo: {"email": "admin@example.com", "password": "secreto"}
        
        2. Otros roles (operador=2, líder=3, conductor=4):
           - Pueden autenticarse usando solo su número de identificación
           - Ejemplo: {"id_number": 1234567890}
        
        La respuesta incluye el token JWT y el rol del usuario autenticado.
        """,
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Autenticación exitosa",
                examples=[
                    OpenApiExample(
                        "Respuesta Admin",
                        value={
                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "rol": 1
                        }
                    ),
                    OpenApiExample(
                        "Respuesta Operador",
                        value={
                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "rol": 2
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Error de validación",
                examples=[
                    OpenApiExample(
                        "Error de campos",
                        value={"detail": "Debe proporcionar email y password, o id_number"},
                        media_type="application/json"
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Error de autenticación",
                examples=[
                    OpenApiExample(
                        "Credenciales inválidas",
                        value={"detail": "Credenciales inválidas"},
                        media_type="application/json"
                    ),
                    OpenApiExample(
                        "Rol incorrecto",
                        value={"detail": "Este método de autenticación es solo para administradores"},
                        media_type="application/json"
                    )
                ]
            )
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            if serializer.validated_data.get('email'):
                # Autenticación admin (User)
                user, is_admin = ServicesUser().authenticate(
                    serializer.validated_data['email'],
                    serializer.validated_data['password']
                )
                auth_obj = user  # Objeto User
            else:
                # Autenticación operador (Person) por código
                person, is_admin = ServicesUser().authenticate_by_code(
                    serializer.validated_data['code']
                )
                auth_obj = person  # Objeto Person

            token = JWTAuthentication.generate_jwt(auth_obj)
            return Response({
                "token": token,
                "isAdmin": is_admin
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(
                {"detail": f"Error en la autenticación {str(e)}"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class UserSoftDelete(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Soft delete administrator",
        description="Soft delete an administrator by marking them as inactive",
        responses={
            200: {"example": {"message": "User soft deleted successfully"}},
            404: {"example": {"error": "User not found"}},
            500: {"example": {"error": "Error deleting user"}}
        }
    )
    def delete(self, request, pk):
        """Soft delete user by ID"""
        user_service = ServicesUser()
        
        success = user_service.soft_delete(pk)
        if success:
            return Response(
                {"message": "User soft deleted successfully"}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "User not found or error deleting user"}, 
            status=status.HTTP_404_NOT_FOUND
        )

class UserReactivate(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Reactivate administrator",
        description="Reactivate a soft deleted administrator",
        responses={
            200: {"example": {"message": "User reactivated successfully"}},
            404: {"example": {"error": "User not found or already active"}},
            500: {"example": {"error": "Error reactivating user"}}
        }
    )
    def patch(self, request, pk):
        """Reactivate soft deleted user"""
        user_service = ServicesUser()
        
        success = user_service.reactivate(pk)
        if success:
            return Response(
                {"message": "User reactivated successfully"}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "User not found or already active"}, 
            status=status.HTTP_404_NOT_FOUND
        )

class UserList(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all users",
        description="List all users with option to include inactive ones",
        parameters=[
            {
                "name": "include_inactive",
                "in": "query",
                "description": "Include inactive users",
                "required": False,
                "schema": {"type": "boolean"}
            }
        ],
        responses={
            200: UserSerializer(many=True)
        }
    )
    def get(self, request):
        """List all users"""
        user_service = ServicesUser()
        include_inactive = request.query_params.get('include_inactive', 'false').lower() == 'true'
        
        users = user_service.list_all(include_inactive=include_inactive)
        serializer = UserSerializer(users, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

