from django.db import models
from django.db.models.query import QuerySet
from api.person.models import Person
from api.utils.s3utils import upload_operator_photo, upload_operator_license_front, upload_operator_license_back
from api.utils.image_processor import ImageProcessor
import logging
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class OperatorQuerySet(QuerySet):
    def active(self):
        """Filtrar solo operadores activos."""
        return self.filter(status='active')

class OperatorManager(models.Manager):
    def get_queryset(self):
        """Retorna un QuerySet personalizado."""
        return OperatorQuerySet(self.model, using=self._db)
    
    def active(self):
        """Retorna solo operadores activos."""
        return self.get_queryset().active()

class Operator(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    id_operator = models.AutoField(primary_key=True)

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name='operator',
        db_column="id_person"
    )

    number_licence = models.CharField(max_length=100, null=True, blank=True)
    # code = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    n_children = models.IntegerField(null=True, blank=True)
    size_t_shift = models.CharField(max_length=20, null=True, blank=True)
    name_t_shift = models.CharField(max_length=100, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Image fields with separate upload paths to avoid conflicts
    photo = models.ImageField(
        upload_to=upload_operator_photo,
        storage=S3Boto3Storage(),
        null=True,
        blank=True
    )
    license_front = models.ImageField(
        upload_to=upload_operator_license_front,
        storage=S3Boto3Storage(),
        null=True,
        blank=True
    )
    license_back = models.ImageField(
        upload_to=upload_operator_license_back,
        storage=S3Boto3Storage(),
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES,
        default='active',
        null=True, 
        blank=True
    )

    # Definir el manager por defecto y el manager personalizado
    objects = OperatorManager()
    all_objects = models.Manager()  # Manager que incluye todos los objetos, activos e inactivos

    def __str__(self):
        return f"Operator {self.id_operator} - {self.person.id_number if self.person else 'No Person Assigned'}"

    class DoesNotExist(Exception):
        pass
    
    def soft_delete(self):
        """Marca el operador como inactivo en lugar de eliminarlo."""
        self.status = 'inactive'
        self.save()

    def save(self, *args, **kwargs):
        # Track if each field has been modified to only compress changed images
        is_new = self._state.adding
        
        # Configure image processor with appropriate prefixes for better organization
        processor = ImageProcessor()
        
        if is_new:
            # For new instances, compress all provided images
            if self.photo:
                logger.debug(f"Compressing new operator photo")
                self.photo = processor.compress_image(self.photo, prefix="operator_photo")
            if self.license_front:
                logger.debug(f"Compressing new operator license front")
                self.license_front = processor.compress_image(self.license_front, prefix="license_front")
            if self.license_back:
                logger.debug(f"Compressing new operator license back")
                self.license_back = processor.compress_image(self.license_back, prefix="license_back")
        else:
            # For updates, only compress images that are being updated
            try:
                old_instance = Operator.all_objects.get(pk=self.pk)
                
                # Check if photo has changed - compare by name to avoid path access
                if self.photo and (not old_instance.photo or self.photo.name != old_instance.photo.name):
                    logger.debug(f"Compressing updated operator photo")
                    self.photo = processor.compress_image(self.photo, prefix="operator_photo")
                    
                # Check if license_front has changed
                if self.license_front and (not old_instance.license_front or self.license_front.name != old_instance.license_front.name):
                    logger.debug(f"Compressing updated operator license front")
                    self.license_front = processor.compress_image(self.license_front, prefix="license_front")
                    
                # Check if license_back has changed
                if self.license_back and (not old_instance.license_back or self.license_back.name != old_instance.license_back.name):
                    logger.debug(f"Compressing updated operator license back")
                    self.license_back = processor.compress_image(self.license_back, prefix="license_back")
                    
            except Operator.DoesNotExist:
                # Fallback if old instance can't be found
                logger.warning(f"Could not find existing Operator with ID {self.pk} for comparison")
                if self.photo:
                    self.photo = processor.compress_image(self.photo, prefix="operator_photo")
                if self.license_front:
                    self.license_front = processor.compress_image(self.license_front, prefix="license_front")
                if self.license_back:
                    self.license_back = processor.compress_image(self.license_back, prefix="license_back")

        super().save(*args, **kwargs)
    