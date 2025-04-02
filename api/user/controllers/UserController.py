from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.person.serializers.PersonSerializer import PersonSerializer

from api.user.serializers.UserSerializer import UserSerializer
from api.user.services.ServicesUser import ServicesUser
from api.user.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.permissions import AllowAny

class UserRegister(APIView):
    permission_classes = [AllowAny]  # <-- Permite acceso sin autenticación
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
    permission_classes = [AllowAny]  # <-- Permite acceso sin autenticación
    authentication_classes = []

    @extend_schema(
        summary="Autenticar usuario",
        description="Requiere email y contraseña. Devuelve token JWT.",
        request=UserSerializer,  # ✅ Serializer con campos requeridos
        responses={
            200: OpenApiResponse(
                description="Token JWT generado",
                examples=[
                    OpenApiExample(
                        "Respuesta exitosa",
                        value={
                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                        },
                        media_type="application/json"
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validación fallida",
                examples=[
                    OpenApiExample(
                        "Ejemplo error 400",
                        value={"detail": "Email y contraseña requeridos"},
                        media_type="application/json"
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Credenciales inválidas",
                examples=[
                    OpenApiExample(
                        "Ejemplo error 401",
                        value={"detail": "Email no registrado"},
                        media_type="application/json"
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Ejemplo request válido",
                value={
                    "email": "maria@example.com",
                    "password": "password123"
                },
                request_only=True,
                media_type="application/json"
            )
        ]
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email y contraseña requeridos"}, 
                status=400
            )

        try:
            user = ServicesUser().authenticate(email, password)
            token = JWTAuthentication.generate_jwt(user)
            return Response({"token": token}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=401)

