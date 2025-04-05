from django.db import models
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.payment.models.Payment import Payment

class Assign(models.Model):
    """
    Model that represents an assignment between an operator, order, truck and payment.
    """
    operator = models.ForeignKey(
        Operator, 
        on_delete=models.CASCADE, 
        related_name="assignments"
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="assignments"
    )
    truck = models.ForeignKey(
        Truck, 
        on_delete=models.CASCADE, 
        related_name="assignments", 
        null=True, 
        blank=True
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        related_name="assignments",
        null=True,
        blank=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    rol = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'api_assign'
        unique_together = ('operator', 'order', 'truck')
        app_label = 'api'

    def __str__(self):
        return f"{self.operator} assigned to {self.order} with {self.truck}"
