from django.db import models
from api.job.models.Job import Job
class Tool(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)  
    name = models.CharField(
        max_length=10, 
        unique=True
    )
    
    job = models.ForeignKey(  # Job realtion
        Job, 
        related_name="tools", 
        on_delete=models.CASCADE,
        db_column="id_job"
    )
    def __str__(self):
        return self.name