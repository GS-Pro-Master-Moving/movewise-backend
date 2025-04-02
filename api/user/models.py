# api/user/models.py
from django.db import models
from api.person.models import Person

class User(models.Model):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True
    )
    user_name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos requeridos por Django
    USERNAME_FIELD = 'user_name'  # Indica qué campo actúa como "username"
    REQUIRED_FIELDS = []  # Campos adicionales para createsuperuser (vacío si no se necesitan)

    def __str__(self):
        return self.user_name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False