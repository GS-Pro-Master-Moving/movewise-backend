from django.db import models
from api.company.models.Company import Company
from api.job.models.Job import Job
class Tool(models.Model):
    id = models.AutoField(
        primary_key=True, 
        db_column="id_tool"
    )
    name = models.CharField(
        max_length=60, 
        #unique=True
    )# Ask for name if it is unique or not
    
    job = models.ForeignKey(  # Job realtion
        Job, 
        related_name="tools", 
        on_delete=models.CASCADE,
        db_column="id_job"
    )
    company = models.ForeignKey(  # Nueva relación con Company
        Company,
        related_name="tools", 
        on_delete=models.CASCADE,  # Si se elimina la compañía, también se eliminan las herramientas
        db_column="id_company"
    )
    state = models.BooleanField(
        default=True, 
        #Valor por defecto True        
        db_column="state_tool"
    )
    def __str__(self):
        return self.name