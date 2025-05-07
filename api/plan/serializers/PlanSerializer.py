from rest_framework import serializers
from api.plan.models.Plan import Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
