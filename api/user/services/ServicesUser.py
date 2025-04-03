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
            user = person.user  
            
            # Check the password using check_password ✅
            if not user.check_password(password):  
                raise ValueError("Incorrect password")
            
            return user
        except Person.DoesNotExist:
            raise ValueError("Email not registered")
        except User.DoesNotExist:
            raise ValueError("User not found")

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