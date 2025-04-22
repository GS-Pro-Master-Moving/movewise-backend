from rest_framework import serializers
from api.son.models import Son

class SonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Son
        fields = '__all__'
