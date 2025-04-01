from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from api.order.serializers.OrderSerializer import OrderSerializer
from api.order.services.ServicesOrder import ServicesOrder  
from api.order.models.Order import Order
from api.job.models.Job import Job

class ControllerOrder(viewsets.ViewSet):
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

    # This decorator customizes the Swagger/OpenAPI documentation for this endpoint.
    # It defines a summary, a detailed description, the type of data expected in the request,
    # and possible response codes with their respective structures.
    @extend_schema(
        summary="Update an existing order",
        description="Updates an order with the given data if the order is not finalized.",
        request=OrderSerializer,
        responses={200: OrderSerializer, 400: {"error": "Invalid data"}, 403: {"error": "Cannot edit finalized order"}}
    )

    #actualizacion parcial --> permite actualizar solo algunos campos del modelo sin necesidad de enviar todos los datos
    #partial update --> allows you to update only some fields of the model without having to send all the data
    
    def partial_update(self, request, pk=None):
        try:
            # Get the order by its key
            order = Order.objects.get(key=pk)
            #validation if the order status is finalized it cannot be updated
            if order.payStatus == 1:
                return Response({
                    "status": "error",
                    "messDev": "Order is finalized and cannot be modified",
                    "messUser": "No se pueden modificar órdenes finalizadas",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

            # the job field is handled
            data = request.data.copy()
            if "job" in data and isinstance(data["job"], (int, str)):
                try:
                    # We just check that it exists, the conversion will be done by the service
                    Job.objects.get(id=data["job"])
                except Job.DoesNotExist:
                    return Response({
                        "status": "error",
                        "messDev": f"Job with ID {data['job']} does not exist",
                        "messUser": "El trabajo especificado no existe",
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Update the order using the service
            updated_order = self.order_service.update_order(order, data)
            
            # Return the response with the updated data
            return Response(OrderSerializer(updated_order).data, status=status.HTTP_200_OK) 
        
        except Order.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Order not found",
                "messUser": "No se encontró la orden",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating order: {str(e)}",
                "messUser": f"No se pudo actualizar la orden: {str(e)}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
