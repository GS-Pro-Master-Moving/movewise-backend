from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from api.subscription.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.subscription.services.SubscriptionService import SubscriptionService

class SubscriptionController(ViewSet):
    service = SubscriptionService()

    def list(self, request):
        subs = self.service.list_subscriptions()
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        sub = self.service.get_subscription(pk)
        if sub:
            serializer = SubscriptionSerializer(sub)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            sub = self.service.create_subscription(serializer.validated_data)
            return Response(SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
