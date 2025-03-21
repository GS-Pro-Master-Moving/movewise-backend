from django.db import models
import uuid
from api.orders.model.Order import Order  

class JobChoices(models.TextChoices):
    C = "c", "C"
    PC = "p/c", "P/C"
    P = "p", "P"
    LOAD = "load", "Load"

class Job(models.Model):
    id_job = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    name = models.CharField(
        max_length=50, 
        choices=JobChoices.choices
    )  
    #id_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="jobs")  

    def __str__(self):
        return f"{self.name}"

