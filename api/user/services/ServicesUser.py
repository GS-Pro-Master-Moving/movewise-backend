from django.contrib.auth.hashers import make_password, check_password
from api.person.models import Person
from api.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.operator.models import Operator

class ServicesUser:
    @staticmethod
    def authenticate(email: str, password: str) -> tuple[User, bool]:
        try:
            person = Person.objects.get(email=email)
            user = person.user
            
            if not user.check_password(password):  
                raise ValueError("Contraseña incorrecta")
            
            return user, True
        except Person.DoesNotExist:
            raise ValueError("Email no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    def authenticate_by_id_number(id_number: int):
        try:
            person = Person.objects.get(id_number=id_number)
            
            # Verificar si es operador
            try:
                operator = Operator.objects.get(person=person)
                return person, False  # Retorna Person y False (no es admin)
            except Operator.DoesNotExist:
                raise ValueError("Usuario no tiene permisos para acceder")
            
        except Person.DoesNotExist:
            raise ValueError("Número de identificación no registrado")

    @staticmethod
    def create_user(person_data: dict, user_data: dict) -> User:
        raw_password = user_data.pop("password")  
        
        person = Person.objects.create(**person_data)
            
        user = User.objects.create_user(
            user_name=user_data["user_name"],
            password=raw_password,  
            **user_data
        )
            
        # Relate Person to User
        person.user = user
        person.save()
            
        return user