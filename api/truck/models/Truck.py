from django.db import models
from api.company.models.Company import Company

class Truck(models.Model):
    id_truck = models.AutoField(primary_key=True) 
    number_truck = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=100) 
    name = models.CharField(max_length=100)  
    status = models.BooleanField(default=True, db_default=True)# True = Active, False = Inactive
    category = models.CharField(max_length=100, null=True, blank=True)  # Optional field for category
    # FK a Company
    id_company = models.ForeignKey(
        Company,
        related_name='trucks',
        on_delete=models.CASCADE,
        db_column='id_company',
        null=False,
        blank=True
    )
    def __str__(self):
        return f"{self.name} ({self.number_truck}) - {self.type}"
    