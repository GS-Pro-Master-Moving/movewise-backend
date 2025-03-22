from rest_framework import status, viewsets
from rest_framework.response import Response
from api.order.serializers.OrderSerializer import OrderSerializer

class OrderController(viewsets.ViewSet):
    
    def create(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)