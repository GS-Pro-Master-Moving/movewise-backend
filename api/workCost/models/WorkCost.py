from django.db import models
from api.order.models.Order import Order
class WorkCost(models.Model):
    id_workCost = models.AutoField(primary_key=True, unique=True, db_column="id_workCost")
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=10)
    id_order = models.ForeignKey(        
        Order,
        related_name='WorkCost',
        on_delete=models.CASCADE,
        db_column='id_order',
        null=True,
        blank=True)
    
    def __str__(self):
        return f"{self.name}"