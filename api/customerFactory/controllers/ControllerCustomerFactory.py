from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.customerFactory.serializers.SerializerCustomerFactory import SerializerCustomerFactory
from api.customerFactory.services.ServiceCustomerFactory import ServicesCustomerFactory
class CustomerFactoryController(viewsets.ViewSet):
    """
    CRUD completo de CustomerFactory.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ServicesCustomerFactory()

    @extend_schema(responses={200: OpenApiResponse(response=SerializerCustomerFactory(many=True))})
    def list(self, request):
        qs = self.service.list()
        return Response(SerializerCustomerFactory(qs, many=True).data)

    @extend_schema(responses={200: OpenApiResponse(response=SerializerCustomerFactory)})
    def retrieve(self, request, pk=None):
        obj = self.service.get(pk)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SerializerCustomerFactory(obj).data)

    @extend_schema(request=SerializerCustomerFactory, responses={201: SerializerCustomerFactory})
    def create(self, request):
        ser = SerializerCustomerFactory(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = self.service.create(ser.validated_data)
        return Response(SerializerCustomerFactory(obj).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=SerializerCustomerFactory, responses={200: SerializerCustomerFactory})
    def partial_update(self, request, pk=None):
        ser = SerializerCustomerFactory(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        obj = self.service.update(pk, ser.validated_data)
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SerializerCustomerFactory(obj).data)

    @extend_schema(responses={204: OpenApiResponse(description="No Content")})
    def destroy(self, request, pk=None):
        deleted = self.service.delete(pk)
        if deleted is None:
            return Response({"error":"Customer factory not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error":"Customer Factory deleted succesfully"}, status=status.HTTP_200_OK)

    @extend_schema(responses={204: OpenApiResponse(description="No Content")})
    def setStateFalse(self, request, pk=None):
        deleted = self.service.setStateFalse(pk)
        if deleted is None:
            return Response({"error":"Customer factory not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error":"Customer Factory deleted succesfully"}, status=status.HTTP_200_OK)
