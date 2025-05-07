from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from api.order.models.Order import StatesUSA  

class OrderStatesController(APIView):
    authentication_classes = [] #null 
    permission_classes = [AllowAny] # no token

    def get(self, request, *args, **kwargs):
        try:
            states = [{'code': s.value, 'name': s.label} for s in StatesUSA]
            return Response(states)
        except Exception as e:
            return Response({
                "status": "error",
                "messDev": f"Error fetching states: {str(e)}",
                "messUser": "Error fetching states",
                "data": None
            }, status=400)
