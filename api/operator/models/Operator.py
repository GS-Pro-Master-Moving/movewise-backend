import uuid
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from api.person.models import Person
from api.utils import upload_operator_file as util_upload_operator_file
class Operator(models.Model):
    upload_operator_file = util_upload_operator_file
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

   #image fields
    photo = models.ImageField(upload_to=upload_operator_file, null=True, blank=True)
    license_front = models.ImageField(upload_to=upload_operator_file, null=True, blank=True)
    license_back = models.ImageField(upload_to=upload_operator_file, null=True, blank=True)

    status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Operator {self.id_operator} - {self.person.id_number if self.person else 'No Person Assigned'}"

    class DoesNotExist(Exception):
        pass

    def compress_image(self, image_field):
        try:
            image = Image.open(image_field)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            buffer = BytesIO()
            image.save(buffer, format='JPEG', optimize=True, quality=60)  # adjust quality
            return ContentFile(buffer.getvalue(), name=image_field.name)
        except Exception as e:
            print(f"Error compressing image: {e}")
            return image_field  # if it fails, use original image

    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = self.compress_image(self.photo)
        if self.license_front:
            self.license_front = self.compress_image(self.license_front)
        if self.license_back:
            self.license_back = self.compress_image(self.license_back)

        super().save(*args, **kwargs)
