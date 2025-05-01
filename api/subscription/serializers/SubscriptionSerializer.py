from rest_framework import serializers
from api.subscription.models.Subscription import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
