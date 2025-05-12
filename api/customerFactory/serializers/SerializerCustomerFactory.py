from rest_framework import serializers
from api.customerFactory.models.CustomerFactory import CustomerFactory

class SerializerCustomerFactory(serializers.ModelSerializer):
    class Meta:
        model = CustomerFactory
        fields = ['id_factory', 'name']
