from django.db import models
from api.subscription.models.Subscription import Subscription

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    license_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_company'
        verbose_name = 'api_company'
        verbose_name_plural = 'Companies'
        app_label = 'api'

    def __str__(self):
        return f"{self.name} - {self.license_number}" 
