from django.db import models
from api.order.models.Order import Order
from api.truck.models.Truck import Truck

class CostFuel(models.Model):
    id_fuel = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='cost_fuels')
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='cost_fuels')
    cost_fuel = models.FloatField()  # Cambiado a numérico
    cost_gl = models.FloatField()     # Cambiado a numérico
    fuel_qty = models.FloatField()    # Cambiado a numérico
    distance = models.FloatField()     # Cambiado a numérico
    
    def __str__(self):
        return f"Fuel {self.id_fuel} - Order: {self.order.key_ref} - Truck: {self.truck.number_truck}"