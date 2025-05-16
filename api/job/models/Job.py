from django.db import models
from api.company.models.Company import Company

class Job(models.Model):
    id = models.AutoField(primary_key=True, editable=False)  
    name = models.CharField(
        max_length=100, 
        unique=True
    )
    # State of the job
    state = models.BooleanField(
        default=True,
        db_column='ACTIVE'
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