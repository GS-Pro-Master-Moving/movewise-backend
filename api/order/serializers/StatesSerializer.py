from rest_framework import serializers

class StatesUSASerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()