# api/authentication.py
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
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")

        # Validate required claims
        required_claims = {'person_id', 'company_id'}
        if not required_claims.issubset(payload.keys()):
            raise AuthenticationFailed("Missing required token claims")

        # Get authenticated entity
        auth_entity = self._get_authenticated_entity(payload)
        if not auth_entity:
            raise AuthenticationFailed("Invalid credentials")

        # Attach company context to request
        request.company_id = payload['company_id']
        return (auth_entity, None)

    def _get_authenticated_entity(self, payload):
        try:
            # Try admin user first
            user = User.objects.select_related('person').get(
                person__id_person=payload['person_id'],
                person__id_company=payload['company_id']
            )
            user.is_admin = True
            return user
        except User.DoesNotExist:
            # Fallback to operator
            try:
                person = Person.objects.select_related('id_company').get(
                    id_person=payload['person_id'],
                    id_company=payload['company_id']
                )
                Operator.objects.get(person=person)
                person.is_admin = False
                return person
            except (Person.DoesNotExist, Operator.DoesNotExist):
                return None

    @staticmethod
    def generate_jwt(obj) -> str:
        """Generate JWT for User (admin) or Person (operator)"""
        now = datetime.datetime.utcnow()
        payload = {
            "exp": now + datetime.timedelta(hours=2),
            "iat": now,
        }

        if isinstance(obj, User) and hasattr(obj, 'person'):
            payload.update({
                "person_id": obj.person.id_person,
                "company_id": obj.person.id_company.id,
                "email": obj.person.email,
                "is_admin": True
            })
        elif isinstance(obj, Person):
            payload.update({
                "person_id": obj.id_person,
                "company_id": obj.id_company.id,
                "email": obj.email or "operator@example.com",
                "is_admin": False
            })
        else:
            raise ValueError("Invalid object type for JWT generation")

        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
