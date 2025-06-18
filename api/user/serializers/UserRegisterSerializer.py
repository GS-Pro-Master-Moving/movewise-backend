from rest_framework import serializers

class UserRegisterSerializer(serializers.Serializer):
    user_name = serializers.CharField()
    password = serializers.CharField()
    person = serializers.DictField()