from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.person.serializers.PersonSerializer import PersonSerializer

from api.user.serializers.UserSerializer import UserSerializer
from api.user.serializers.LoginSerializer import LoginSerializer
from api.user.serializers.LoginResponseSerializer import LoginResponseSerializer
from api.user.services.ServicesUser import ServicesUser
from api.user.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.permissions import AllowAny

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
        # The data should include "person" as a dictionary inside "user"
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                # Autenticación por email/password
                user = ServicesUser().authenticate(
                    serializer.validated_data['email'],
                    serializer.validated_data['password']
                )
            else:
                # Autenticación por id_number
                user = ServicesUser().authenticate_by_id_number(
                    serializer.validated_data['id_number']
                )

            token = JWTAuthentication.generate_jwt(user)
            response_data = {
                "token": token,
                "rol": user.person.id_rol
            }
            
            response_serializer = LoginResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(
                {"detail": "Error en la autenticación"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

