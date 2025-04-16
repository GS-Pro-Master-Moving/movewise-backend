from rest_framework import serializers
from api.costFuel.models.CostFuel import CostFuel
from api.order.serializers.OrderSerializer import OrderSerializer
from api.truck.serializers.SerializerTruck import SerializerTruck

class SerializerCostFuel(serializers.ModelSerializer):
    """
    Serializer for the CostFuel model.
    """
    class Meta:
        model = CostFuel
        fields = ['id_fuel', 'order', 'truck', 'cost_fuel', 'cost_gl', 'fuel_qty', 'distance']

class SerializerCostFuelDetail(serializers.ModelSerializer):
    """
    Detailed serializer for the CostFuel model with expanded relationships.
    """
    order = OrderSerializer(read_only=True)
    truck = SerializerTruck(read_only=True)
    
    class Meta:
        model = CostFuel
        fields = ['id_fuel', 'order', 'truck', 'cost_fuel', 'cost_gl', 'fuel_qty', 'distance']