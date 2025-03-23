from rest_framework import serializers
from api.operator.models.Operator import Operator

class SerializerOperator(serializers.ModelSerializer):
    """
    Serializer for the Operator model.

    This serializer includes all fields of the Operator model.
    """

    class Meta:
        model = Operator
        fields = "__all__"
