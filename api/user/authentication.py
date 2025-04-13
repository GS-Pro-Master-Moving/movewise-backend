# api/user/authentication.py
import jwt
import datetime
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import User
from api.person.models import Person
from api.operator.models import Operator

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        token = auth_header.split("Bearer ")[-1] if "Bearer " in auth_header else auth_header

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Buscar User (admin)
            try:
                user = User.objects.get(person__id_person=payload["person_id"])
                return (user, None)
            except User.DoesNotExist:
                # Buscar Operator
                try:
                    person = Person.objects.get(id_person=payload["person_id"])
                    Operator.objects.get(person=person)  # Verifica que exista el operador
                    return (person, None)
                except (Person.DoesNotExist, Operator.DoesNotExist):
                    raise AuthenticationFailed("Acceso no autorizado")
                
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado")
        except Exception as e:
            raise AuthenticationFailed(f"Token inválido: {str(e)}")

    @staticmethod
    def generate_jwt(obj) -> str:
        """Genera token para User (Admin) o Person (Operator)"""
        if hasattr(obj, 'person'):  # Es un User (Admin)
            payload = {
                "person_id": obj.person.id_person,
                "email": obj.person.email,
                "is_admin": True,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
                "iat": datetime.datetime.utcnow()
            }
        elif hasattr(obj, 'id_person'):  # Es una Person (Operator)
            payload = {
                "person_id": obj.id_person,
                "email": obj.email or "operador@empresa.com",
                "is_admin": False,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
                "iat": datetime.datetime.utcnow()
            }
        else:
            raise ValueError("Se requiere objeto User o Person para generar token")
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")