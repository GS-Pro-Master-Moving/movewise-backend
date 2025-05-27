# api/user/models.py
from django.contrib.auth.hashers import make_password
from django.db import models
from api.person.models import Person
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from api.company.models.Company import Company
from django.db.models.query import QuerySet
from api.utils.image_processor import ImageProcessor
from storages.backends.s3boto3 import S3Boto3Storage
from api.utils.s3utils import upload_user_photo

import logging

logger = logging.getLogger(__name__)

class UserQuerySet(QuerySet):
    def active(self):
        """Filtrar solo usuarios activos (basado en el status de Person)"""
        return self.filter(person__status='active')

class UserManager(BaseUserManager):
    #new methods
    def get_queryset(self):
        """return custom queryset"""
        return UserQuerySet(self.model, using=self._db)
    
    def active(self):
        """return active user"""
        return self.get_queryset().active()

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
    photo = models.ImageField(upload_to=upload_user_photo,storage=S3Boto3Storage(),null=True,blank=True,max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id_company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column="id_company")
    # required fields for django
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = []

    objects = UserManager()  
    all_objects = models.Manager()

    class Meta:
        app_label = 'api'
        db_table = 'api_user'  # name of the table

    def __str__(self):
        return self.user_name
    
    def soft_delete(self):
        "Marks the user as inactive using their associated persona."
        if self.person:
            self.person.soft_delete()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        proccessor  = ImageProcessor()

        if is_new:
            #for new instances, compress
            if self.photo:
                logger.debug(f'compressing new user photo')
                self.photo = proccessor.compress_image(self.photo, prefix='user_photo')
        else:
            try:
                old_instance = User.all_objects.get(pk=self.pk)

                if self.photo and (not old_instance.photo or self.photo.name != old_instance.photo.name):
                    logger.debug(f"Compressing updated user photo")
                    self.photo = proccessor.compress_image(self.photo, prefix="user_photo")
                    
            except User.DoesNotExist:
                logger.debug(f'could not find user with ID')
                if self.photo:
                    self.photo = proccessor.compress_image(self.photo, prefix='user_photo')
        super().save(*args, **kwargs)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        """User is active if their associated person is active"""
        return self.person.status == 'active' if self.person else False