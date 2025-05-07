from rest_framework import serializers

class SerializerOperatorUpdate(serializers.Serializer):
    """
    Serializer for updating a specific field of an operator.

    Fields:
    - new_value (str): The new value for the field.
    """
    new_value = serializers.CharField(max_length=100)
