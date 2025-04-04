# api/user/authentication.py
import jwt
import datetime
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        token = auth_header.split("Bearer ")[-1] if "Bearer " in auth_header else auth_header

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(person__id_person=payload["person_id"])  # Accede al User via Person
            return (user, None)  # Retorna (user, auth) para DRF
        except Exception as e:
            raise AuthenticationFailed("Token inválido")

    @staticmethod
    def generate_jwt(user: User) -> str:
        payload = {
            "person_id": user.person.id_person,  # Usa el ID de Person
            "email": user.person.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")