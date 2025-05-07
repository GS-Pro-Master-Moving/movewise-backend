import uuid
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from api.person.models import Person
from api.utils import upload_operator_photo,upload_operator_license_front,upload_operator_license_back

class Operator(models.Model):
    id_operator = models.AutoField(primary_key=True)

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name='operator',
        db_column="id_person"
    )

    number_licence = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    n_children = models.IntegerField(null=True, blank=True)
    size_t_shift = models.CharField(max_length=20, null=True, blank=True)
    name_t_shift = models.CharField(max_length=100, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Image fields with separate upload paths to avoid conflicts
    photo = models.ImageField(
        upload_to=upload_operator_photo,
        null=True,
        blank=True
    )
    license_front = models.ImageField(
        upload_to=upload_operator_license_front,
        null=True,
        blank=True
    )
    license_back = models.ImageField(
        upload_to=upload_operator_license_back,
        null=True,
        blank=True
    )

    status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Operator {self.id_operator} - {self.person.id_number if self.person else 'No Person Assigned'}"

    class DoesNotExist(Exception):
        pass

    def compress_image(self, image_field):
        if not image_field:
            return image_field
            
        try:
            # Check if this is a newly uploaded file or an existing one
            if hasattr(image_field, 'path'):
                image = Image.open(image_field.path)
            else:
                image = Image.open(image_field)
                
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            buffer = BytesIO()
            image.save(buffer, format='JPEG', optimize=True, quality=60)  # adjust quality
            
            # Create a new filename to avoid cache issues
            original_name = os.path.basename(image_field.name)
            new_name = f"{uuid.uuid4()}.jpg"
            
            return ContentFile(buffer.getvalue(), name=new_name)
        except Exception as e:
            print(f"Error compressing image: {e}")
            return image_field  # if it fails, use original image

    def save(self, *args, **kwargs):
        # Track if each field has been modified to only compress changed images
        is_new = self._state.adding
        
        if is_new:
            # For new instances, compress all provided images
            if self.photo:
                self.photo = self.compress_image(self.photo)
            if self.license_front:
                self.license_front = self.compress_image(self.license_front)
            if self.license_back:
                self.license_back = self.compress_image(self.license_back)
        else:
            # For updates, only compress images that are being updated
            try:
                old_instance = Operator.objects.get(pk=self.pk)
                
                # Check if photo has changed
                if self.photo and self.photo != old_instance.photo:
                    self.photo = self.compress_image(self.photo)
                    
                # Check if license_front has changed
                if self.license_front and self.license_front != old_instance.license_front:
                    self.license_front = self.compress_image(self.license_front)
                    
                # Check if license_back has changed
                if self.license_back and self.license_back != old_instance.license_back:
                    self.license_back = self.compress_image(self.license_back)
                    
            except Operator.DoesNotExist:
                # Fallback if old instance can't be found
                if self.photo:
                    self.photo = self.compress_image(self.photo)
                if self.license_front:
                    self.license_front = self.compress_image(self.license_front)
                if self.license_back:
                    self.license_back = self.compress_image(self.license_back)

        super().save(*args, **kwargs)