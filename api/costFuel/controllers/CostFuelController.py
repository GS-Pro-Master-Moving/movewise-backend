from rest_framework import status, viewsets, pagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from api.costFuel.services.ServicesCostFuel import ServicesCostFuel

from api.costFuel.serializers.SerializerCostFuel import SerializerCostFuel, SerializerCostFuelDetail
from api.costFuel.models.CostFuel import CostFuel

class ControllerCostFuel(viewsets.ViewSet):
    """
    Controller for managing cost fuel records.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cost_fuel_service = ServicesCostFuel()

    @extend_schema(
        summary="Get all cost fuel records",
        description="Retrieves all cost fuel records with pagination.",
        responses={
            200: OpenApiResponse(
                response=SerializerCostFuel(many=True),
                description="Cost fuel records retrieved successfully"
            )
        }
    )
    def list(self, request):
        """
        Returns a paginated list of all cost fuel records.
        """
        try:
            cost_fuels = self.cost_fuel_service.get_all()
            
            # Pagination setup
            paginator = pagination.PageNumberPagination()
            paginator.page_size = request.query_params.get("page_size", 10)
            paginated_cost_fuels = paginator.paginate_queryset(cost_fuels, request)
            
            return paginator.get_paginated_response({
                "status": "success",
                "messDev": "Cost fuel records fetched",
                "messUser": "Registros de costo de combustible obtenidos",
                "data": SerializerCostFuel(paginated_cost_fuels, many=True).data
            })
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching cost fuel records: {str(e)}",
                "messUser": "No se pudieron obtener los registros de costo de combustible",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get cost fuel by ID",
        description="Retrieves a cost fuel record by its ID.",
        responses={
            200: OpenApiResponse(
                response=SerializerCostFuelDetail,
                description="Cost fuel record retrieved successfully"
            ),
            404: OpenApiResponse(
                description="Cost fuel record not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Cost fuel record not found"}
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """
        Returns a cost fuel record by its ID.
        """
        try:
            cost_fuel = self.cost_fuel_service.get_by_id(pk)
            if cost_fuel:
                return Response({
                    "status": "success",
                    "messDev": "Cost fuel record retrieved",
                    "messUser": "Registro de costo de combustible obtenido",
                    "data": SerializerCostFuelDetail(cost_fuel).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "messDev": "Cost fuel record not found",
                    "messUser": "Registro de costo de combustible no encontrado",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error retrieving cost fuel record: {str(e)}",
                "messUser": "No se pudo obtener el registro de costo de combustible",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get cost fuels by order",
        description="Retrieves cost fuel records associated with an order.",
        responses={
            200: OpenApiResponse(
                response=SerializerCostFuel(many=True),
                description="Cost fuel records retrieved successfully"
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_key>[^/.]+)')
    def by_order(self, request, order_key=None):
        """
        Returns cost fuel records associated with an order.
        """
        try:
            cost_fuels = self.cost_fuel_service.get_by_order(order_key)
            
            # Pagination setup
            paginator = pagination.PageNumberPagination()
            paginator.page_size = request.query_params.get("page_size", 10)
            paginated_cost_fuels = paginator.paginate_queryset(cost_fuels, request)
            
            return Response({
                "status": "success",
                "messDev": "Cost fuel records for order fetched",
                "messUser": "Registros de costo de combustible para la orden obtenidos",
                "data": SerializerCostFuel(paginated_cost_fuels, many=True).data
            })
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching cost fuel records for order: {str(e)}",
                "messUser": "No se pudieron obtener los registros de costo de combustible para la orden",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get cost fuels by truck",
        description="Retrieves cost fuel records associated with a truck.",
        responses={
            200: OpenApiResponse(
                response=SerializerCostFuel(many=True),
                description="Cost fuel records retrieved successfully"
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='by-truck/(?P<truck_id>\d+)')
    def by_truck(self, request, truck_id=None):
        """
        Returns cost fuel records associated with a truck.
        """
        try:
            cost_fuels = self.cost_fuel_service.get_by_truck(truck_id)
            
            # Pagination setup
            paginator = pagination.PageNumberPagination()
            paginator.page_size = request.query_params.get("page_size", 10)
            paginated_cost_fuels = paginator.paginate_queryset(cost_fuels, request)
            
            return paginator.get_paginated_response({
                "status": "success",
                "messDev": "Cost fuel records for truck fetched",
                "messUser": "Registros de costo de combustible para el camión obtenidos",
                "data": SerializerCostFuel(paginated_cost_fuels, many=True).data
            })
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching cost fuel records for truck: {str(e)}",
                "messUser": "No se pudieron obtener los registros de costo de combustible para el camión",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Create cost fuel record",
        description="Creates a new cost fuel record.",
        request=SerializerCostFuel,
        responses={
            201: OpenApiResponse(
                response=SerializerCostFuel,
                description="Cost fuel record created successfully"
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"error": "Validation error"}
                    )
                ]
            )
        }
    )
    def create(self, request):
        """
        Creates a new cost fuel record.
        Expected payload:
        {
            "order": "order_uuid",
            "truck": 1,
            "cost_fuel": 100.00,
            "cost_gl": 3.50,
            "fuel_qty": 28.57,
        }
        """
        serializer = SerializerCostFuel(data=request.data)
        if serializer.is_valid():
            try:
                cost_fuel = self.cost_fuel_service.create_cost_fuel(serializer.validated_data)
                return Response({
                    "status": "success",
                    "messDev": "Cost fuel record created successfully",
                    "messUser": "El registro de costo de combustible ha sido creado",
                    "data": SerializerCostFuel(cost_fuel).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "status": "error",
                    "messDev": f"Error creating cost fuel record: {str(e)}",
                    "messUser": "Hubo un problema al crear el registro de costo de combustible",
                    "data": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "status": "error",
            "messDev": "Validation error",
            "messUser": "Datos inválidos",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update cost fuel record",
        description="Updates an existing cost fuel record.",
        request=SerializerCostFuel,
        responses={
            200: OpenApiResponse(
                response=SerializerCostFuel,
                description="Cost fuel record updated successfully"
            ),
            404: OpenApiResponse(
                description="Cost fuel record not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Cost fuel record not found"}
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """
        Updates an existing cost fuel record.
        Expected payload:
        {
            "order": "order_uuid",
            "truck": 1,
            "cost_fuel": 120.00,
            "cost_gl": 4.00,
            "fuel_qty": 30.0,
        }
        """
        try:
            cost_fuel = get_object_or_404(CostFuel, id_fuel=pk)
            serializer = SerializerCostFuel(cost_fuel, data=request.data, partial=True)
            if serializer.is_valid():
                updated_cost_fuel = self.cost_fuel_service.update_cost_fuel(pk, serializer.validated_data)
                if updated_cost_fuel:
                    return Response({
                        "status": "success",
                        "messDev": "Cost fuel record updated successfully",
                        "messUser": "El registro de costo de combustible ha sido actualizado",
                        "data": SerializerCostFuel(updated_cost_fuel).data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "status": "error",
                        "messDev": "Cost fuel record not found",
                        "messUser": "Registro de costo de combustible no encontrado",
                        "data": None
                    }, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "status": "error",
                "messDev": "Validation error",
                "messUser": "Datos inválidos",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating cost fuel record: {str(e)}",
                "messUser": "No se pudo actualizar el registro de costo de combustible",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Delete cost fuel record",
        description="Deletes a cost fuel record by its ID.",
        responses={
            204: OpenApiResponse(
                description="Cost fuel record deleted successfully"
            ),
            404: OpenApiResponse(
                description="Cost fuel record not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Cost fuel record not found"}
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """
        Deletes a cost fuel record by its ID.
        """
        try:
            deleted = self.cost_fuel_service.delete_cost_fuel(pk)
            if deleted:
                return Response({
                    "status": "success",
                    "messDev": "Cost fuel record deleted successfully",
                    "messUser": "El registro de costo de combustible ha sido eliminado",
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({
                    "status": "error",
                    "messDev": "Cost fuel record not found",
                    "messUser": "Registro de costo de combustible no encontrado",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error deleting cost fuel record: {str(e)}",
                "messUser": "No se pudo eliminar el registro de costo de combustible",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)