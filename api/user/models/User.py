# api/user/models.py
from django.contrib.auth.hashers import make_password
from django.db import models
from api.person.models import Person
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, user_name, password=None, **extra_fields):
        print(f'print en Create_user: {password}')
        if not user_name:
            raise ValueError("El user_name es obligatorio")
        user = self.model(user_name=user_name, **extra_fields)
        if password and not password.startswith('pbkdf2_sha256$'):
            print('bandera 2')
            password = make_password(password)
        user.password = password
        user.save(using=self._db)
        return user


    def create_superuser(self, user_name, password=None, **extra_fields):
        # Implementa esto si usas createsuperuser
        extra_fields.setdefault("is_staff", True)
        return self.create_user(user_name, password, **extra_fields)

class User(AbstractBaseUser): 
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True
    )
    user_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos requeridos por Django
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = []

    objects = UserManager()  

    def __str__(self):
        return self.user_name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False