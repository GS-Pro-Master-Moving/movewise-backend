from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from api.job.services.ServicesJob import ServicesJob
from api.job.serializers.SerializerJob import SerializerJob

class JobController(viewsets.ViewSet):
    """
    Controller for managing Job entities.

    Provides an endpoint for:
    - Retrieving all jobs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_service = ServicesJob()  # Service instance

    @extend_schema(
        summary="Retrieve all jobs",
        description="Returns a list of all jobs stored in the database.",
        responses={200: OpenApiResponse(response=SerializerJob(many=True))},
    )
    def list(self, request):
        """
        Retrieve all jobs.

        Returns:
        - 200 OK: A list of Job objects serialized as JSON.
        """
        jobs = self.job_service.get_all_jobs()  # Calls service to get all jobs
        return Response(SerializerJob(jobs, many=True).data)

    