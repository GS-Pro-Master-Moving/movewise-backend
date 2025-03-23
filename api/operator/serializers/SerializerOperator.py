from rest_framework import serializers
from api.operator.models.Operator import Operator

class SerializerOperator(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = "__all__"
