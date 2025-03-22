from rest_framework import status, viewsets
from rest_framework.response import Response
from api.job.services.ServicesJob import ServicesJob
from api.job.serializers.SerializerJob import SerializerJob

class JobController(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_service = ServicesJob()  # Instancia del servicio

    def list(self, request):
        """Obtiene todos los Jobs"""
        jobs = self.job_service.get_all_jobs()  # Llama al servicio para obtener todos los jobs
        return Response(SerializerJob(jobs, many=True).data)  # Serializa y responde
