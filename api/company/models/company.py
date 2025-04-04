from django.db import models
from api.user.models.User import User
from api.order.models.Order import Order

class Company(models.Model):
    license_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relación con User
    id_user = models.ForeignKey(
        User,
        related_name='companies',
        on_delete=models.CASCADE,
        db_column='id_user'
    )
    
    # Relación con Order
    id_order = models.ForeignKey(
        Order,
        related_name='companies',
        on_delete=models.CASCADE,
        db_column='id_order',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'Company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        app_label = 'api'  # Especificar explícitamente la aplicación

    def __str__(self):
        return f"{self.name} - {self.license_number}" 