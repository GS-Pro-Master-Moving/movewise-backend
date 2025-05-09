from django.db import models
from api.company.models.Company import Company

class Job(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)  
    name = models.CharField(
        max_length=10, 
        unique=True
    )

    # FK a Company
    id_company = models.ForeignKey(
        Company,
        related_name='jobs',
        on_delete=models.CASCADE,
        db_column='id_company',
        null=False,
        blank=True
    )

    def __str__(self):
        return self.name