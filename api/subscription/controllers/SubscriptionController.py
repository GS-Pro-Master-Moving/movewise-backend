from rest_framework import viewsets, status
from rest_framework.response import Response

from api.subscription.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.subscription.services.SubscriptionService import SubscriptionService

class SubscriptionController(viewsets.ViewSet):

    def list(self, request):
        subscriptions = SubscriptionService.list_subscriptions()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        subscription = SubscriptionService.retrieve_subscription(pk)
        if subscription:
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        return Response({'detail': 'Subscription not found.'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subscription = SubscriptionService.create_subscription(serializer.validated_data)
            return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        subscription = SubscriptionService.retrieve_subscription(pk)
        if not subscription:
            return Response({'detail': 'Subscription not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            updated_subscription = SubscriptionService.update_subscription(subscription, serializer.validated_data)
            return Response(SubscriptionSerializer(updated_subscription).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        subscription = SubscriptionService.retrieve_subscription(pk)
        if not subscription:
            return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
        
        SubscriptionService.delete_subscription(subscription)
        return Response({"detail": "Subscription deleted successfully."}, status=status.HTTP_200_OK)
