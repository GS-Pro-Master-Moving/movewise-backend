from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.job.services.ServicesJob import ServicesJob
from api.job.serializers.SerializerJob import SerializerJob

class JobController(viewsets.ViewSet):
    """
    Job's complete CRUD.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_service = ServicesJob()

    @extend_schema(
        summary="List all jobs that are active",
        responses={200: OpenApiResponse(response=SerializerJob(many=True))}
    )
    def list(self, request):
        jobs = self.job_service.get_all_jobs()
        return Response(SerializerJob(jobs, many=True).data)

    @extend_schema(
        summary="Retrieve a job by ID",
        responses={200: OpenApiResponse(response=SerializerJob)}
    )
    def retrieve(self, request, pk=None):
        job = self.job_service.get_job(pk)
        if not job:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SerializerJob(job).data)

    @extend_schema(
        summary="Create a new job",
        request=SerializerJob,
        responses={201: OpenApiResponse(response=SerializerJob)}
    )
    def create(self, request):
        company_id = getattr(request, 'company_id', None)
        serializer = SerializerJob(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = self.job_service.create_job(serializer.validated_data, company_id)
        return Response(SerializerJob(job).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Partially update a job",
        request=SerializerJob,
        responses={200: OpenApiResponse(response=SerializerJob)}
    )
    def partial_update(self, request, pk=None):
        serializer = SerializerJob(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        job = self.job_service.update_job(pk, serializer.validated_data)
        if not job:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SerializerJob(job).data)

    @extend_schema(
        summary="Set state of a job inactive",
        request=SerializerJob,
        responses={200: OpenApiResponse(response=SerializerJob)}
    )
    def set_inactive(self, request, pk=None):
        serializer = SerializerJob(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        print("pk:", pk)
        job = self.job_service.set_inactive(pk)
        if not job:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SerializerJob(job).data)
    @extend_schema(
        summary="delete a job",
        responses={204: OpenApiResponse(description="No Content")}
    )
    def destroy(self, request, pk=None):
        result = self.job_service.delete_job(pk)
        if result is None:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        # result == True
        return Response({"message": "Job deleted successfully"}, status=status.HTTP_200_OK)
