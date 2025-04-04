from django.db import models

class Company(models.Model):
    id_company = models.AutoField(primary_key=True)
    license = models.CharField(max_length=50, null=True, blank=True)# ask for the license
    name = models.CharField(max_length=100, null=True, blank=True)