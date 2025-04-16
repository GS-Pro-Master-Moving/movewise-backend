from rest_framework import viewsets, pagination
from rest_framework.response import Response
from api.workCost.models.WorkCost import WorkCost
from api.workCost.serializers.SerializerWorkCost import SerializerTruck

class WorkCostPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ControllerWorkCost(viewsets.ModelViewSet):
    queryset = WorkCost.objects.all()
    serializer_class = SerializerTruck
    pagination_class = WorkCostPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)