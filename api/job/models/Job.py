from django.db import models

class Job(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)  
    name = models.CharField(
        max_length=10, 
        unique=True
    )

    def __str__(self):
        return self.name