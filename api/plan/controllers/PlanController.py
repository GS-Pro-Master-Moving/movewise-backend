from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from api.plan.serializers.PlanSerializer import PlanSerializer
from api.plan.services.PlanServices import PlanService

from rest_framework import pagination, status
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PlanController(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PlanService()
        self.paginator = CustomPagination()

    @extend_schema(
        summary="Get all plans",
        description="Retrieve a paginated list of all available plans.",
        responses={200: PlanSerializer(many=True)}
    )
    def list(self, request):
        try:
            queryset = self.service.list_plans()
            page = self.paginator.paginate_queryset(queryset, request)
            serializer = PlanSerializer(page, many=True)
            paginated_response = self.paginator.get_paginated_response(serializer.data)
            paginated_data = paginated_response.data
            return Response({
                "message": "Plans retrieved successfully",
                "data": paginated_data,
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": f"Error retrieving plans: {str(e)}",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def retrieve(self, request, pk=None):
        plan = self.service.get_plan(pk)
        if plan:
            serializer = PlanSerializer(plan)
            return Response({
                "status": "success",
                "messDev": "Plan found",
                "messUser": "Plan loaded successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "messDev": "Plan not found",
            "messUser": "Plan does not exist",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Create a new plan",
        description="Creates a new subscription plan with the provided data.",
        request=PlanSerializer,
        responses={
            201: OpenApiResponse(response=PlanSerializer, description="Plan created successfully"),
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request):
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            plan = self.service.create_plan(serializer.validated_data)
            return Response({
                "status": "success",
                "messDev": "Plan created",
                "messUser": "Plan created successfully",
                "data": PlanSerializer(plan).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "messDev": "Validation error",
            "messUser": "Please check the submitted fields",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a plan by ID",
        description="Deletes a specific plan by its ID.",
        responses={
            204: OpenApiResponse(description="Plan deleted successfully"),
            404: OpenApiResponse(description="Plan not found")
        }
    )
    def destroy(self, request, pk=None):
        deleted = self.service.delete_plan(pk)
        if deleted:
            return Response({
                "status": "success",
                "messDev": "Plan deleted",
                "messUser": "Plan deleted successfully",
                "data": None
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({
            "status": "error",
            "messDev": "Plan not found",
            "messUser": "Cannot delete: plan not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Partially update a plan",
        description="Updates only the specified fields of a plan.",
        request=PlanSerializer,
        responses={
            200: OpenApiResponse(response=PlanSerializer, description="Plan updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Plan not found")
        }
    )
    def partial_update(self, request, pk=None):
        serializer = PlanSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            updated_plan = self.service.update_plan_partial(pk, serializer.validated_data)
            if updated_plan:
                return Response({
                    "status": "success",
                    "messDev": "Plan updated",
                    "messUser": "Plan updated successfully",
                    "data": PlanSerializer(updated_plan).data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "error",
                "messDev": "Plan not found for update",
                "messUser": "Plan not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": "error",
            "messDev": "Validation failed for partial update",
            "messUser": "Please check the fields you are trying to update",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
