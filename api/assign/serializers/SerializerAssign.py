from rest_framework import serializers
from api.assign.models.Assign import Assign

class SerializerAssign(serializers.ModelSerializer):
    class Meta:
        model = Assign
        fields = "__all__"
