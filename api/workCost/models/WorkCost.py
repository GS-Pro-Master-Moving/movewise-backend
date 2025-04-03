from django.db import models
from api.order.models.Order import Order

class WorkCost(models.Model):
    id_workCost = models.AutoField(primary_key=True, editable=False)  
    
    name = models.CharField(max_length=100)
    cost = models.DecimalField()
    # In BD diagram its called type but django doesnt suggest this name so I called it cost_type
    cost_type = models.CharField(max_length=100)
    
    id_order = models.ForeignKey( # Order realtion
        Order, 
        related_name='WorkCost', 
        on_delete=models.CASCADE,
        db_column="id_order"  
    )