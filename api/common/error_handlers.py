from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Cases not explicitly handled by DRF
    if isinstance(exc, Http404):
        return Response({'detail': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, PermissionDenied):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)

    return Response({'detail': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def custom_400_handler(request, exception):
    return JsonResponse({'error': 'Bad Request (400)'}, status=400)

def custom_403_handler(request, exception):
    return JsonResponse({'error': 'Forbidden (403)'}, status=403)

def custom_404_handler(request, exception):
    return JsonResponse({'error': 'Not Found (404)'}, status=404)

def custom_500_handler(request):
    return JsonResponse({'error': 'Server Error (500)'}, status=500)

