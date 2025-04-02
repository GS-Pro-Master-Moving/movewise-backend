from django.contrib.auth.hashers import make_password, check_password
from api.user.models import User
from api.person.models import Person
from django.core.exceptions import ObjectDoesNotExist

class ServicesUser:
    @staticmethod
    def authenticate(email: str, password: str) -> User:
        try:
            person = Person.objects.get(email=email)
            user = person.user  # Accede al User desde Person
            # if not check_password(password, user.password):
            if not password == user.password:
                raise ValueError("Contraseña incorrecta")
            return user
        except Person.DoesNotExist:
            raise ValueError("Email no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    def create_user(person_data: dict, user_data: dict) -> User:
        # Hashear la contraseña
        user_data["password"] = make_password(user_data["password"])
        
        # Crear Person y User
        person = Person.objects.create(**person_data)
        user = User.objects.create(**user_data)
        person.user = user  # Establece la relación inversa
        person.save()
        return user