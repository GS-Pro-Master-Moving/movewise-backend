from django.db import models

class Company(models.Model):
    license_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.name} - {self.license_number}" 