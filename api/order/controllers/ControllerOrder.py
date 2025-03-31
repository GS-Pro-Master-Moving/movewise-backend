from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.order.serializers.SerializerOrder import SerializerOrder
from api.order.services.ServicesOrder import ServicesOrder  

class ControllerOrder(viewsets.ViewSet):
    """
    Controller for managing Order entities.

    Provides an endpoint for:
    - Creating an order.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service = ServicesOrder()  

    def create(self, request):
        """
        Create a new order.

        Expects:
        - A JSON body with order details.

        Returns:
        - 201 Created: If the order is successfully created.
        - 400 Bad Request: If the request contains invalid data.
        """
        serializer = SerializerOrder(data=request.data)
        if serializer.is_valid():
            order = self.order_service.create_order(serializer.validated_data) 
            return Response(SerializerOrder(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
