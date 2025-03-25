from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.order.serializers.OrderSerializer import OrderSerializer
from api.order.services.ServicesOrder import ServicesOrder  

class OrderController(viewsets.ViewSet):
    """
    Controller for managing Order entities.

    Provides an endpoint for:
    - Creating an order.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service = ServicesOrder()  

    @extend_schema(
        summary="Create a new order",
        description="Creates an order with the given data and returns the created entity.",
        request=OrderSerializer,
        responses={201: OrderSerializer, 400: {"error": "Invalid data"}}
    )
    def create(self, request):
        """
        Create a new order.

        Expects:
        - A JSON body with order details.

        Returns:
        - 201 Created: If the order is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = self.order_service.create_order(serializer.validated_data) 
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
