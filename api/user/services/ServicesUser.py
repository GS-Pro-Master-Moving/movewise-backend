from django.contrib.auth.hashers import make_password, check_password
from api.person.models import Person
from api.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.operator.models import Operator
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class ServicesUser:
    @staticmethod
    def authenticate(email: str, password: str) -> tuple[User, bool]:
        try:
            person = Person.objects.active().get(email=email)
            user = person.user
            
            if not user.check_password(password):  
                raise ValueError("Contraseña incorrecta")
            
            return user, True
        except Person.DoesNotExist:
            raise ValueError("Email no registrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")

    @staticmethod
    def authenticate_by_code(code: str):
        try:
            # Buscar operador por su código
            operator = Operator.objects.get(code=code)
            
            # Verificar que el operador esté activo
            if operator.person.status != 'active':
                raise ValueError("El operador no está activo")
                
            return operator.person, False  # Retorna Person y False (no es admin)
            
        except Operator.DoesNotExist:
            raise ValueError("Código de operador no válido")

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
    def get_by_id(self, user_id):
        """Get user by person ID (since person is the primary key)"""
        try:
            return User.objects.active().get(person__id_person=user_id)
        except User.DoesNotExist:
            return None
        
    def soft_delete(self, user_id):
        """Soft delete user by marking associated person as inactive"""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            with transaction.atomic():
                user.soft_delete()
                logger.info(f"User {user_id} soft deleted successfully")
                return True
        except Exception as e:
            logger.error(f"Error soft deleting user {user_id}: {str(e)}")
            return False
        
    def reactivate(self, user_id):
        """Reactivate a soft deleted user"""
        try:
            # Use all_objects to find inactive users
            user = User.all_objects.get(person__id_person=user_id)
            if user.person.status == 'inactive':
                user.person.status = 'active'
                user.person.save()
                logger.info(f"User {user_id} reactivated successfully")
                return True
            return False
        except User.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error reactivating user {user_id}: {str(e)}")
            return False