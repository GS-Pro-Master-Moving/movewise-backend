# api/user/models.py
from django.contrib.auth.hashers import make_password
from django.db import models
from api.person.models import Person
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from api.company.models.Company import Company

class UserManager(BaseUserManager):
    def create_user(self, user_name, password=None, **extra_fields):
        if not user_name:
            raise ValueError("the user_name field is required")
        user = self.model(user_name=user_name, **extra_fields)
        if password and not password.startswith('pbkdf2_sha256$'):
            password = make_password(password)
        user.password = password
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, password=None, **extra_fields):
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
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column="id_company")
    # required fields for django
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = []

    objects = UserManager()  

    class Meta:
        app_label = 'api'
        db_table = 'api_user'  # name of the table

    def __str__(self):
        return self.user_name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False