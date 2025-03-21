from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from api.orders.servicesLayer.services.OrderService import OrderService

class OrderController(APIView):
    """ Controller for handling HTTP requests related to orders """

    def post(self, request):
        """
        Creates a new order.
        """
        try:
            order = OrderService.create_order(request.data)
            return Response(
                {"message": "Order created successfully", "order": str(order.data)},  
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


