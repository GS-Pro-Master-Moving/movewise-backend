from api.orders.repository.OrderRepository import OrderRepository
from django.core.exceptions import ValidationError
from api.orders.servicesLayer.dtos.PostOrderDTO import PostOrderDTO

class OrderService:
    """ Service for handling business logic related to orders. """

    def create_order(order_data: dict) -> PostOrderDTO:
        serializer = PostOrderDTO(data=order_data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)  

        order = OrderRepository().create(serializer.validated_data)
        return PostOrderDTO.from_model(order)

