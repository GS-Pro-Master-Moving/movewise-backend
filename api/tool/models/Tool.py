from django.db import models
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
    def __str__(self):
        return self.name