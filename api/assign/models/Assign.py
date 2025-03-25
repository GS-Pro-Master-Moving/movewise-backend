from django.db import models
from api.operator.models.Operator import Operator
from api.order.models.Order import Order

class Assign(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name="assignments", db_column="id_operator")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="assignments", db_column="key")  

    assigned_at = models.DateTimeField(auto_now_add=True) 
    rol = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('operator', 'order')  # Avoid duplicates

    def __str__(self):
        return f"{self.operator} assigned to {self.order}"
