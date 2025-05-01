from rest_framework import viewsets, pagination
from rest_framework.response import Response
from api.workCost.models.WorkCost import WorkCost
from api.workCost.serializers.SerializerWorkCost import SerializerTruck

class WorkCostPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'current_company_id': getattr(self.request, 'company_id', None),
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class ControllerWorkCost(viewsets.ModelViewSet):
    queryset = WorkCost.objects.all()
    serializer_class = SerializerTruck
    pagination_class = WorkCostPagination

    def list(self, request, *args, **kwargs):
        company_id = getattr(request, 'company_id', None)
        if not company_id:
            return Response({"detail": "No company ID provided"}, status=400)

        queryset = self.get_queryset().filter(id_order__id_company=company_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            if hasattr(self, 'paginator'):
                self.paginator.request = request
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "current_company_id": company_id,
            "results": serializer.data
        })
    
    def listByOrderId(self, request, *args, **kwargs):
        """
        Retrieves a paginated list of WorkCost entries filtered by order_id.

        Returns:
        - 200 OK: A paginated list of WorkCost entries.
        - 404 Not Found: If no WorkCost entries are found for the given order_id.
        """
        order_id = kwargs.get('order_id')  
        print("order_id: ", order_id)
        try:
            # Filter WorkCost entries by order_id
            queryset = WorkCost.objects.filter(id_order=order_id)

            # Paginate the queryset
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # If no pagination is applied, return all results
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=200)

        except WorkCost.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"No WorkCost entries found for order_id: {order_id}"
            }, status=404)
            
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)
    
    def bulk_create(self, request, *args, **kwargs):
        """
        Create multiple WorkCost entries in bulk.

        Returns:
        - 201 Created: A list of created WorkCost entries.
        - 400 Bad Request: If the input data is invalid.
        """
        try:
            # Validate the input data
            if not isinstance(request.data, list):
                return Response({"error": "Invalid data format. Expected a list."}, status=400)

            for item in request.data:
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        finally:
            return Response({"messageDev": "WorkCost entries created successfully"},
                            status=201)