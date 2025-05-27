from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import User
from api.person.models import Person
from api.user.serializers.UserSerializer import UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from api.user.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from django.db.models import Q
import uuid
from django.core.files.base import ContentFile
import base64
from rest_framework.parsers import JSONParser
from django.core.files.storage import default_storage
from rest_framework.exceptions import APIException
import binascii
from api.utils.s3utils import upload_user_photo

class UserDetailUpdate(APIView):
    """
    Controller for retrieving user details and partially updating information.
    Supports GET and PATCH operations on the User and Person models.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Get user details",
        description="Retrieves detailed information about a user including their person data.",
        responses={
            200: UserSerializer,
            404: {"example": {"error": "User not found"}}
        },
        examples=[
            OpenApiExample(
                "Successful response example",
                value={
                    "user_name": "admin_user",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "person": {
                        "first_name": "Admin",
                        "last_name": "User",
                        "email": "admin@example.com",
                        "birth_date": "1985-05-15",
                        "phone": 3101234567,
                        "address": "Admin Street 123",
                        "id_number": "1122334455",
                        "type_id": "ID Card"
                    }
                },
                response_only=True
            )
        ]
    )
    def get(self, request, pk=None):
        try:
            if pk:
                user = User.objects.get(person__id_person=pk)
            else:
                user = request.user if isinstance(request.user, User) else None
                
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Limpieza de foto fantasma
            if user.photo:
                try:
                    if not default_storage.exists(user.photo.name):
                        user.photo = None
                        user.save(update_fields=['photo'])
                except Exception as e:
                    print(f"Error en limpieza de foto: {str(e)}")
                    
            return Response(UserSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary="Partial update user information",
        description="""
        Updates user and associated person information. Only provided fields will be updated.
        
        Notes:
        - To update password, include 'password' field with the new password
        - If email is updated, user session will be invalidated
        - Email and id_number are unique and cannot be duplicated
        """,
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: {"example": {"error": "Invalid data"}},
            404: {"example": {"error": "User not found"}},
            409: {"example": {"error": "Email or id_number already exists"}}
        },
        examples=[
            OpenApiExample(
                "Request example (update password)",
                value={
                    "password": "new_password123"
                },
                request_only=True
            ),
            OpenApiExample(
                "Request example (update user and person)",
                value={
                    "user_name": "updated_username",
                    "password": "new_password123",
                    "person": {
                        "email": "updated@example.com",
                        "first_name": "UpdatedName",
                        "last_name": "UpdatedLastName",
                        "birth_date": "1990-01-01",
                        "phone": 3105551234,
                        "address": "New Address 123"
                    }
                },
                request_only=True
            )
        ]
    )
    @transaction.atomic
    def patch(self, request, pk=None):
        try:
            # Obtener usuario
            user = None
            if pk:
                user = User.objects.get(person__id_person=pk)
            else:
                user = request.user if isinstance(request.user, User) else None
                
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 1. Verificación y limpieza inicial de foto fantasma
            if user.photo:
                try:
                    if not default_storage.exists(user.photo.name):
                        user.photo = None
                        user.save(update_fields=['photo'])
                except Exception as e:
                    print(f"Error en verificación inicial de foto: {str(e)}")
                    # No detenemos el proceso, solo registramos el error

            # 2. Procesar campos del usuario
            user_data = {}
            update_user_fields = []
            has_photo_update = False

            # User name
            if 'user_name' in request.data:
                user_data['user_name'] = request.data.get('user_name')
                update_user_fields.append('user_name')

            # Password
            if 'password' in request.data and request.data.get('password'):
                password = request.data.get('password')
                if not password.startswith('pbkdf2_sha256$'):
                    user_data['password'] = make_password(password)
                else:
                    user_data['password'] = password
                update_user_fields.append('password')

            # Photo handling
            if 'photo' in request.data:
                photo_data = request.data['photo']
                
                if photo_data is None or photo_data == '':
                    user.photo = None
                elif isinstance(photo_data, str) and photo_data.startswith('data:image'):
                    try:
                        format_part, data_part = photo_data.split(';base64,')
                        ext = format_part.split('/')[-1].split('+')[0]
                        decoded_file = base64.b64decode(data_part)
                        
                        # Solo crear el ContentFile y asignarlo - el modelo hace el resto
                        user.photo = ContentFile(decoded_file, name=f"temp.{ext}")
                        
                    except Exception as e:
                        return Response({"error": "Invalid image data"}, status=400)
                
                update_user_fields.append('photo')
            # Actualizar campos de usuario
            if user_data:
                for key, value in user_data.items():
                    setattr(user, key, value)
            
            # Guardar cambios de usuario si existen
            if update_user_fields or has_photo_update:
                user.save(update_fields=list(set(update_user_fields)))

            # 3. Procesar campos de persona
            person_data = {}
            email_changed = False
            update_person_fields = []
            
            if 'person' in request.data and isinstance(request.data['person'], dict):
                person = user.person
                person_fields = [
                    'first_name', 'last_name', 'birth_date', 'phone', 
                    'address', 'id_number', 'type_id', 'email'
                ]
                
                for field in person_fields:
                    if field in request.data['person']:
                        new_value = request.data['person'][field]
                        current_value = getattr(person, field)
                        
                        if new_value != current_value:
                            # Validar email único
                            if field == 'email':
                                if Person.objects.filter(email=new_value).exclude(id_person=person.id_person).exists():
                                    return Response(
                                        {"error": "Email already in use"}, 
                                        status=status.HTTP_409_CONFLICT
                                    )
                                email_changed = True
                            
                            # Validar id_number único
                            if field == 'id_number':
                                if Person.objects.filter(id_number=new_value).exclude(id_person=person.id_person).exists():
                                    return Response(
                                        {"error": "ID number already in use"}, 
                                        status=status.HTTP_409_CONFLICT
                                    )
                            
                            setattr(person, field, new_value)
                            update_person_fields.append(field)

                # Guardar cambios de persona si existen
                if update_person_fields:
                    person.save(update_fields=update_person_fields)

            # 4. Verificación final de integridad de foto
            try:
                if user.photo and not default_storage.exists(user.photo.name):
                    user.photo = None
                    user.save(update_fields=['photo'])
            except Exception as e:
                print(f"Error en verificación final de foto: {str(e)}")

            # 5. Preparar respuesta
            user.refresh_from_db()  # Asegurar datos actualizados
            response_data = UserSerializer(user, context={'request': request}).data
            
            if email_changed:
                response_data["session_invalidated"] = True
                response_data["message"] = "Email updated. Please login again with your new credentials."

            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            error_message = str(e)
            # Filtrar mensajes sensibles
            if "password" in error_message.lower():
                error_message = "Error processing request"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
class AdminUserDetailUpdate(APIView):
    """
    Controller for retrieving and updating admin user details.
    Includes additional permission checks to ensure that only admins can access this functionality.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get admin user details",
        description="Retrieves detailed information about an admin user.",
        responses={
            200: UserSerializer,
            403: {"example": {"error": "Not authorized"}},
            404: {"example": {"error": "Admin user not found"}}
        },
        examples=[
            OpenApiExample(
                "Successful response example",
                value={
                    "user_name": "admin_user",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "person": {
                        "first_name": "Admin",
                        "last_name": "User",
                        "email": "admin@example.com",
                        "birth_date": "1985-05-15",
                        "phone": 3101234567,
                        "address": "Admin Street 123",
                        "id_number": "1122334455",
                        "type_id": "ID Card"
                    }
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        try:
            # Check if the current user is an admin
            current_user = request.user
            
            # Assuming isAdmin is a property or field that identifies admin users
            # You might need to adjust this based on how you identify admin users
            if not hasattr(current_user, 'is_staff') or not current_user.is_staff:
                return Response({"error": "Not authorized to access admin information"}, 
                                status=status.HTTP_403_FORBIDDEN)
            
            # Get the admin user (could be the current user or another admin)
            # This assumes you want to get the current admin's details
            admin_user = User.objects.get(person__id_person=current_user.person.id_person)
            
            return Response(UserSerializer(admin_user).data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Update admin user information",
        description="""
        Updates admin user and associated person information. Only provided fields will be updated.
        
        Notes:
        - To update password, include 'password' field with the new password
        - If email is updated, user session will be invalidated
        - Email and id_number are unique and cannot be duplicated
        """,
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: {"example": {"error": "Invalid data"}},
            403: {"example": {"error": "Not authorized"}},
            404: {"example": {"error": "Admin user not found"}},
            409: {"example": {"error": "Email or id_number already exists"}}
        },
        examples=[
            OpenApiExample(
                "Request example (update password)",
                value={
                    "password": "new_admin_password123"
                },
                request_only=True
            ),
            OpenApiExample(
                "Request example (full update)",
                value={
                    "user_name": "updated_admin",
                    "password": "new_admin_password",
                    "person": {
                        "email": "admin_updated@example.com",
                        "first_name": "AdminUpdated",
                        "last_name": "UserUpdated"
                    }
                },
                request_only=True
            )
        ]
    )
    @transaction.atomic
    def patch(self, request):
        try:
            # Check if the current user is an admin
            current_user = request.user
            
            if not hasattr(current_user, 'is_staff') or not current_user.is_staff:
                return Response({"error": "Not authorized to update admin information"}, 
                                status=status.HTTP_403_FORBIDDEN)
            
            # Get the admin user
            admin_user = User.objects.get(person__id_person=current_user.person.id_person)
            
            # Update logic similar to UserDetailUpdate.patch but for admin
            user_data = {}
            person_data = {}
            email_changed = False
            
            # Extract user fields to update
            if 'user_name' in request.data:
                user_data['user_name'] = request.data.get('user_name')
                
            # Handle password update
            if 'password' in request.data and request.data.get('password'):
                password = request.data.get('password')
                if not password.startswith('pbkdf2_sha256$'):
                    user_data['password'] = make_password(password)
                else:
                    user_data['password'] = password
            
            # Extract person fields to update
            if 'person' in request.data and isinstance(request.data.get('person'), dict):
                person_fields = [
                    'first_name', 'last_name', 'birth_date', 'phone', 
                    'address', 'id_number', 'type_id', 'email'
                ]
                for field in person_fields:
                    if field in request.data.get('person'):
                        # Check if email is changing
                        if field == 'email':
                            new_email = request.data.get('person').get('email')
                            if new_email != admin_user.person.email:
                                # Check if new email already exists
                                if Person.objects.filter(email=new_email).exclude(id_person=admin_user.person.id_person).exists():
                                    return Response(
                                        {"error": "Email already registered to another user"}, 
                                        status=status.HTTP_409_CONFLICT
                                    )
                                email_changed = True
                        
                        # Check if id_number is changing and if it's unique
                        if field == 'id_number':
                            new_id_number = request.data.get('person').get('id_number')
                            if new_id_number and new_id_number != admin_user.person.id_number:
                                # Check if new id_number already exists
                                if Person.objects.filter(id_number=new_id_number).exclude(id_person=admin_user.person.id_person).exists():
                                    return Response(
                                        {"error": "ID number already registered to another user"}, 
                                        status=status.HTTP_409_CONFLICT
                                    )
                        
                        person_data[field] = request.data.get('person').get(field)
            
            # Update user if there are user fields to update
            if user_data:
                for key, value in user_data.items():
                    setattr(admin_user, key, value)
                admin_user.save()
            
            # Update person if there are person fields to update
            if person_data:
                person = admin_user.person
                for key, value in person_data.items():
                    setattr(person, key, value)
                person.save()
            
            response_data = UserSerializer(admin_user).data
            
            # If email changed, indicate that session should be invalidated
            if email_changed:
                response_data["session_invalidated"] = True
                response_data["message"] = "Email updated. Please login again with your new credentials."
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)