from rest_framework import viewsets, status
from rest_framework.response import Response
from api.operator.serializers.SerializerOperator import OperatorSerializer
from api.operator.services.ServiceOperator import OperatorService

class OperatorViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OperatorService()

    def create(self, request):
        serializer = OperatorSerializer(data=request.data)
        if serializer.is_valid():
            operator = self.service.create_operator(serializer.validated_data)
            return Response(OperatorSerializer(operator).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
