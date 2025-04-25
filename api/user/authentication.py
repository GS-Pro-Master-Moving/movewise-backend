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
            
            # Search User (admin)
            try:
                user = User.objects.get(person__id_person=payload["person_id"])
                return (user, None)
            except User.DoesNotExist:
                # Search Operator
                try:
                    person = Person.objects.get(id_person=payload["person_id"])
                    Operator.objects.get(person=person)  
                    return (person, None)
                except (Person.DoesNotExist, Operator.DoesNotExist):
                    raise AuthenticationFailed("Unauthorized access")
                
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except Exception as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")

    @staticmethod
    def generate_jwt(obj) -> str:
        "Generate token for User (Admin) or Person (Operator)"
        if hasattr(obj, 'person'):  # Es un User (Admin)
            company_id = obj.person.id_company.id
            payload = {
                "person_id": obj.person.id_person,
                "company_id": company_id,
                "email": obj.person.email,
                "is_admin": True,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                "iat": datetime.datetime.utcnow()
            }
        elif hasattr(obj, 'id_person'):  # Is a Person (Operator)
            company_id = obj.id_company.id
            payload = {
                "person_id": obj.id_person,
                "company_id": company_id,
                "email": obj.email or "operador@empresa.com",
                "is_admin": False,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                "iat": datetime.datetime.utcnow()
            }
        else:
            raise ValueError("Se requiere objeto User o Person para generar token")
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")