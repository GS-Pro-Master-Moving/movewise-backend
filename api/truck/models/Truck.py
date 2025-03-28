from django.db import models

class Truck(models.Model):
    id_truck = models.AutoField(primary_key=True) 
    number_truck = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=100) 
    rol = models.CharField(max_length=100)  
    name = models.CharField(max_length=100)  
    status = models.BooleanField(default=True, db_default=True)# True = Active, False = Inactive
    def __str__(self):
        return f"{self.name} ({self.number_truck}) - {self.type}"
