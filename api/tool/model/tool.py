import uuid
from django.db import models
from api.job.model.job import Job  

class Tool(models.Model):
    id_tool = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) 
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="tools")

    def __str__(self):
        return f"{self.name} (Job: {self.job.id_job})"
