from django.contrib.auth.hashers import make_password, check_password  # Importa check_password
from api.person.models import Person
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()  # Obtiene el modelo User activo (custom o default)

class ServicesUser:
    @staticmethod
    def authenticate(email: str, password: str) -> User:
        try:
            person = Person.objects.get(email=email)
            user = person.user  # Accede al User desde Person
            
            # Verifica la contraseña usando check_password ✅
            if not user.check_password(password):  # Compara hash vs texto plano
                raise ValueError("Contraseña incorrecta")
            
            return user
        except Person.DoesNotExist:
            raise ValueError("Email no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    def create_user(person_data: dict, user_data: dict) -> User:
        raw_password = user_data.pop("password")  # Extrae la contraseña
        
        # Crea laj Persona
        person = Person.objects.create(**person_data)
            
        # Crea el User usando el manager personalizado (hashea la contraseña)
        user = User.objects.create_user(
            user_name=user_data["user_name"],
            password=raw_password,  # ✅ set_password() se encarga del hash
            **user_data
        )
            
        # Relaciona Person con User
        person.user = user
        person.save()
            
        return user