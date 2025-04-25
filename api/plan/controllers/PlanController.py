from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from api.plan.serializers.PlanSerializer import PlanSerializer
from api.plan.services.PlanServices import PlanService

class PlanController(ViewSet):
    service = PlanService()

    def list(self, request):
        plans = self.service.list_plans()
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        plan = self.service.get_plan(pk)
        if plan:
            serializer = PlanSerializer(plan)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            plan = self.service.create_plan(serializer.validated_data)
            return Response(PlanSerializer(plan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
