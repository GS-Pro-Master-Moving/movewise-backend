from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from api.models import User
from api.person.models import Person
from api.person.serializers.PersonSerializer import PersonSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db import IntegrityError
import hashlib
import logging
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    photo = Base64ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = User
        fields = ('user_name', 'password', 'person', 'photo', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'user_name': {'validators': []} 
        }

    def get_photo(self, obj):
        if obj.photo:
            try:
                # Verificar existencia real en S3
                if default_storage.exists(obj.photo.name):
                    return self.context['request'].build_absolute_uri(obj.photo.url)
                # Si no existe, limpiar referencia
                obj.photo = None
                obj.save(update_fields=['photo'])
                return None
            except Exception as e:
                print(f"Error verificando foto: {str(e)}")
                return None
        return None

    def validate_user_name(self, value):
        # Verificar username en usuarios activos
        if User.objects.filter(user_name=value, person__status='active').exists():
            raise serializers.ValidationError("Nombre de usuario ya registrado")
        return value

    def validate(self, data):
        person_data = data.get('person', {})
        email = person_data.get('email')
        id_number = person_data.get('id_number')
        company = person_data.get('id_company')

        # Validar contra registros ACTIVOS
        active_persons = Person.objects.active()
        
        if active_persons.filter(email=email).exists():
            raise serializers.ValidationError({
                "person": {"email": "Email ya registrado (activo)"}
            })
            
        if active_persons.filter(id_number=id_number).exists():
            raise serializers.ValidationError({
                "person": {"id_number": "Número de identificación ya registrado (activo)"}
            })

        return data
    def create(self, validated_data):
        person_data = validated_data.pop('person')
        user_name = validated_data['user_name']
        password = validated_data.pop('password')
        photo = validated_data.get('photo')
        company = person_data.get('id_company')
        email = person_data.get('email')
        id_number = person_data.get('id_number')

        try:
            with transaction.atomic():
                # Buscar persona inactiva con email o id_number
                inactive_person = Person.all_objects.filter(
                    (Q(email=email) | Q(id_number=id_number)),
                    status='inactive'
                ).first()

                if inactive_person:
                    # Validar unicidad en activos excluyendo el registro actual
                    if Person.objects.active().filter(email=email).exclude(pk=inactive_person.pk).exists():
                        raise serializers.ValidationError({"person": {"email": "Email ya registrado en otro usuario activo"}})
                    
                    if Person.objects.active().filter(id_number=id_number).exclude(pk=inactive_person.pk).exists():
                        raise serializers.ValidationError({"person": {"id_number": "Número de identificación ya registrado en otro usuario activo"}})

                    # Reactivar y actualizar persona
                    inactive_person.status = 'active'
                    inactive_person.__dict__.update(**{
                        k: v for k, v in person_data.items()
                        if k not in ['email', 'id_number']  # Campos únicos no modificables
                    })
                    inactive_person.id_company = company
                    inactive_person.save()

                    # Manejo inteligente de la foto
                    user = inactive_person.user
                    current_photo = user.photo
                    
                    if photo:
                        # Calcular hash de nueva foto
                        new_content = photo.read()
                        photo.seek(0)
                        new_hash = hashlib.md5(new_content).hexdigest()
                        
                        # Calcular hash de foto existente si hay
                        current_hash = None
                        if current_photo:
                            try:
                                current_content = current_photo.read()
                                current_hash = hashlib.md5(current_content).hexdigest()
                            except Exception as e:
                                logger.error(f"Error leyendo foto existente: {str(e)}")
                        
                        # Actualizar solo si es diferente
                        if new_hash != current_hash:
                            user.photo = photo
                    else:
                        user.photo = current_photo  # Mantener foto existente

                    # Actualizar datos del usuario
                    user.user_name = user_name
                    user.set_password(password)
                    user.id_company = company
                    user.save()
                    
                    return user

                # Validación final para nuevos registros
                if Person.objects.filter(email=email).exists():
                    raise serializers.ValidationError({"person": {"email": "Email ya registrado"}})
                    
                if Person.objects.filter(id_number=id_number).exists():
                    raise serializers.ValidationError({"person": {"id_number": "Número de identificación ya registrado"}})

                # Crear nuevo usuario
                person = Person.objects.create(**person_data, status='active')
                user = User.objects.create(
                    person=person,
                    user_name=user_name,
                    id_company=company,
                    photo=photo
                )
                user.set_password(password)
                user.save()
                return user

        except IntegrityError as e:
            error_mapping = {
                'email': ("person", "email", "Email ya existe en otro registro"),
                'id_number': ("person", "id_number", "Número de identificación ya existe en otro registro"),
                'user_name': ("user_name", "", "Nombre de usuario ya está en uso")
            }
            
            for db_field, (field, nested_field, message) in error_mapping.items():
                if db_field in str(e):
                    if nested_field:
                        raise serializers.ValidationError({field: {nested_field: [message]}})
                    else:
                        raise serializers.ValidationError({field: [message]})
            
            raise serializers.ValidationError({"detail": "Error de integridad en la base de datos"})