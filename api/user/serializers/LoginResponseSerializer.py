from rest_framework import serializers

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    rol = serializers.IntegerField()
    
    class Meta:
        fields = ('token', 'rol') 