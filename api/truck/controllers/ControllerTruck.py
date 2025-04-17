from rest_framework import status, viewsets, pagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.truck.serializers.SerializerUpdateTruck import SerializerUpdateTruck
from api.truck.services.ServicesTruck import ServicesTruck
from api.truck.serializers.SerializerTruck import SerializerTruck
from api.truck.models.Truck import Truck
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
class ControllerTruck(viewsets.ViewSet):
    """
    Controller for managing trucks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.truck_service = ServicesTruck()  # Instancia del servicio


    @extend_schema(
        summary="Get truck by ID",
        description="Retrieves a truck by its ID.",
        responses={
            200: OpenApiResponse(
                response=SerializerTruck,   
                description="Truck retrieved successfully"
            ),
            404: OpenApiResponse(
                description="Truck not found",
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"error": "Truck not found"}
                    )
                ]
            )
        }
    )   
    def get_truck_by_id(self, request, id_truck):
        try:
            truck = Truck.objects.get(id_truck=id_truck)
            return Response(SerializerTruck(truck).data, status=status.HTTP_200_OK)
        except Truck.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Truck not found",
                "messUser": "Camión no encontrado",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)    
        

    def get_avaliable(self, request):
        """
        Returns a paginated list of available (active) trucks.
        """
        try:
            trucks = self.truck_service.get_avaliable()

            # Paginación manual con PageNumberPagination
            paginator = pagination.PageNumberPagination()
            paginator.page_size = request.query_params.get("page_size", 10)  # Tamaño configurable
            paginated_trucks = paginator.paginate_queryset(trucks, request)

            return paginator.get_paginated_response({
                "status": "success",
                "messDev": "Available trucks fetched",
                "messUser": "Camiones disponibles obtenidos",
                "data": SerializerTruck(paginated_trucks, many=True).data
            })

        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching available trucks: {str(e)}",
                "messUser": "No se pudieron obtener los camiones disponibles",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """
        Creates a new truck.
        Expected payload:
        {
            "number_truck": "ABC123",
            "type": "Cargo",
            "rol": "Transport",
            "name": "Big Truck"
        }
        """
        serializer = SerializerTruck(data=request.data)
        if serializer.is_valid():
            try:
                truck = self.truck_service.create_truck(serializer.validated_data)
                return Response({
                    "status": "success",
                    "messDev": "Truck created successfully",
                    "messUser": "El camión ha sido registrado",
                    "data": SerializerTruck(truck).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "status": "error",
                    "messDev": f"Error creating truck: {str(e)}",
                    "messUser": "Hubo un problema al registrar el camión",
                    "data": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "status": "error",
            "messDev": "Validation error",
            "messUser": "Datos inválidos",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update_status(self, request, pk=None):
        """
        Activates or deactivates a truck.
        Expected payload:
        {
            "status": true  # true for active, false for inactive
        }
        """
        try:
            truck = self.truck_service.update_status(pk, request.data.get("status"))
            return Response({
                "status": "success",
                "messDev": "Truck status updated",
                "messUser": f"El camión ha sido {'activado' if truck.status else 'desactivado'}",
                "data": SerializerTruck(truck).data
            }, status=status.HTTP_200_OK)
        except Truck.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Truck not found",
                "messUser": "No se encontró el camión",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error updating truck status: {str(e)}",
                "messUser": "No se pudo actualizar el estado del camión",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_truck(self, request, pk=None):
        """
        Updates a truck's details.
        Expected payload:
        {
            "number_truck": "DEF456",
            "type": "Carga mediana",
            "name": "Truck 3",
            "category": null
        }
        """
        try:
            truck = get_object_or_404(Truck, id_truck=pk)
            serializer = SerializerUpdateTruck(truck, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "messDev": "Truck updated successfully",
                    "messUser": "El camión ha sido actualizado",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "error",
                "messDev": "Validation error",
                "messUser": "Datos inválidos",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Truck.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Truck not found",
                "messUser": "No se encontró el camión",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
            
    def delete_truck(self, request, pk=None):
        """
        Deletes a truck by its ID.
        """
        try:
            truck = get_object_or_404(Truck, id_truck=pk)
            truck.delete()
            return Response({
                "status": "success",
                "messDev": "Truck deleted successfully",
                "messUser": "El camión ha sido eliminado",
                "data": None
            }, status=status.HTTP_204_NO_CONTENT)
        except Truck.DoesNotExist:
            return Response({
                "status": "error",
                "messDev": "Truck not found",
                "messUser": "No se encontró el camión",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)