from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.son.serializers.SerializerSon import SonSerializer
from api.son.services.ServiceSon import SonService
from rest_framework import status, viewsets, pagination

class SonController(viewsets.ViewSet):

    def get(self, request, son_id=None):
        if son_id:
            son = SonService.get_son(son_id)
            if son:
                serializer = SonSerializer(son)
                return Response(serializer.data)
            return Response({'error': 'Hijo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            sons = SonService.list_son()
            serializer = SonSerializer(sons, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = SonSerializer(data=request.data)
        if serializer.is_valid():
            hijo = SonService.create_son(serializer.validated_data)
            return Response(SonSerializer(hijo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, son_id):
        son = SonService.get_son(son_id)
        if not son:
            return Response({'error': 'Hijo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SonSerializer(son, data=request.data, partial=True)
        if serializer.is_valid():
            actualizado = SonService.update_son(son, serializer.validated_data)
            return Response(SonSerializer(actualizado).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, son_id):
        son = SonService.get_son(son_id)
        if not son:
            return Response({'error': 'Son not Found'}, status=status.HTTP_404_NOT_FOUND)

        SonService.delete_son(son)
        return Response({'success':'delete success'},status=status.HTTP_204_NO_CONTENT)
