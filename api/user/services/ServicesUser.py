from django.contrib.auth.hashers import make_password, check_password
from api.person.models import Person
from api.models import User
from django.core.exceptions import ObjectDoesNotExist

class ServicesUser:
    @staticmethod
    def authenticate(email: str, password: str) -> tuple[User, bool]:
        """
        Autenticación para administradores usando email y password
        Retorna una tupla (user, is_admin)
        """
        try:
            person = Person.objects.get(email=email)
            user = person.user  
            
            # Si se autentica con email y password, es admin
            if not user.check_password(password):  
                raise ValueError("Contraseña incorrecta")
            
            return user, True  # Es admin porque usa email/password
        except Person.DoesNotExist:
            raise ValueError("Email no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    def authenticate_by_id_number(id_number: int) -> tuple[User, bool]:
        """
        Autenticación para no-administradores usando número de identificación
        Retorna una tupla (user, is_admin)
        """
        try:
            person = Person.objects.get(id_number=id_number)
            user = person.user
            return user, False  # No es admin porque usa id_number
        except Person.DoesNotExist:
            raise ValueError("Número de identificación no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

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