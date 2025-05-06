
import logging
import traceback

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)
def custom_exception_handler(exc, context):
    #1) Let DRF handle known exceptions first
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    tb = traceback.format_exc()
    logger.error("Unhandled exception in %s:\n%s", context.get('view'), tb)

    # Building a more detailed payload
    detail = {
        "type": exc.__class__.__name__,
        "message": str(exc),
    }

    if isinstance(exc, DRFValidationError):
        detail["errors"] = exc.detail

    if isinstance(exc, Http404):
        status_code = status.HTTP_404_NOT_FOUND
        detail["message"] = "Resource not found"
    elif isinstance(exc, PermissionDenied):
        status_code = status.HTTP_403_FORBIDDEN
        detail["message"] = "Permission denied"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(detail, status=status_code)


def custom_400_handler(request, exception):
    return JsonResponse({'error': 'Bad Request (400)'}, status=400)

def custom_403_handler(request, exception):
    return JsonResponse({'error': 'Forbidden (403)'}, status=403)

def custom_404_handler(request, exception):
    return JsonResponse({'error': 'Not Found (404)'}, status=404)

def custom_500_handler(request):
    return JsonResponse({'error': 'Server Error (500)'}, status=500)

