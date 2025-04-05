from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from api.payment.models.Payment import Payment
from api.payment.serializers.PaymentSerializer import PaymentSerializer, PaymentAuditSerializer
from api.payment.services.ServicesPayment import ServicesPayment

class ControllerPayment(ViewSet):
    """
    API endpoints to manage payments.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = ServicesPayment()

    @extend_schema(
        summary="List all payments",
        description="Get a list of all payments registered in the system.",
        responses={
            200: OpenApiResponse(
                response=PaymentSerializer(many=True),
                description="Payment list retrieved successfully"
            )
        }
    )
    def list(self, request):
        """
        List all payments.
        """
        payments = self.payment_service.list_payments()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get a specific payment",
        description="Get the details of a specific payment using its ID.",
        responses={
            200: OpenApiResponse(
                response=PaymentSerializer,
                description="Payment found successfully"
            ),
            404: OpenApiResponse(
                description="Payment not found",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={
                            "status": "error",
                            "messDev": "Payment not found",
                            "messUser": "Payment not found",
                            "data": None
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """
        Get a payment by its ID.
        """
        payment = self.payment_service.get_payment(pk)
        if not payment:
            return Response({
                "status": "error",
                "messDev": "Payment not found",
                "messUser": "Payment not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new payment",
        description="Create a new payment record with the provided data.",
        request=PaymentSerializer,
        responses={
            201: OpenApiResponse(
                response=PaymentSerializer,
                description="Payment created successfully"
            ),
            400: OpenApiResponse(
                description="Invalid data",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "status": "error",
                            "messDev": "Invalid data",
                            "messUser": "Invalid data",
                            "data": {
                                "amount": ["This field is required"],
                                "status": ["Invalid payment status"]
                            }
                        }
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "amount": 1500.00,
                    "status": "pending",
                    "date_payment": "2024-03-15T10:30:00Z",
                    "bonus": 100.00,
                    "payment_method": "credit_card",
                    "notes": "Payment for moving service"
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        """
        Create a new payment.
        """
        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "messDev": "Invalid data",
                "messUser": "Invalid data",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = self.payment_service.create_payment(serializer.validated_data)
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({
                "status": "error",
                "messDev": str(e),
                "messUser": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an existing payment",
        description="Update the data of an existing payment identified by its ID.",
        request=PaymentSerializer,
        responses={
            200: OpenApiResponse(
                response=PaymentSerializer,
                description="Payment updated successfully"
            ),
            404: OpenApiResponse(
                description="Payment not found",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={
                            "status": "error",
                            "messDev": "Payment not found",
                            "messUser": "Payment not found",
                            "data": None
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid data or payment not modifiable",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "status": "error",
                            "messDev": "Cannot modify a completed payment",
                            "messUser": "Cannot modify a completed payment",
                            "data": None
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """
        Update an existing payment.
        """
        serializer = PaymentSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "messDev": "Invalid data",
                "messUser": "Invalid data",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = self.payment_service.update_payment(pk, serializer.validated_data)
            if not payment:
                return Response({
                    "status": "error",
                    "messDev": "Payment not found",
                    "messUser": "Payment not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            return Response(PaymentSerializer(payment).data)
        except ValueError as e:
            return Response({
                "status": "error",
                "messDev": str(e),
                "messUser": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a payment",
        description="Delete an existing payment if it's not completed.",
        responses={
            204: OpenApiResponse(
                description="Payment deleted successfully"
            ),
            404: OpenApiResponse(
                description="Payment not found",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={
                            "status": "error",
                            "messDev": "Payment not found",
                            "messUser": "Payment not found",
                            "data": None
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Cannot delete payment",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={
                            "status": "error",
                            "messDev": "Cannot delete completed payments",
                            "messUser": "Cannot delete completed payments",
                            "data": None
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """
        Delete a payment.
        """
        try:
            if self.payment_service.delete_payment(pk):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                "status": "error",
                "messDev": "Payment not found",
                "messUser": "Payment not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                "status": "error",
                "messDev": str(e),
                "messUser": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get payment audit history",
        description="Get the record of changes made to a specific payment.",
        responses={
            200: OpenApiResponse(
                response=PaymentAuditSerializer(many=True),
                description="Audit history retrieved successfully"
            ),
            404: OpenApiResponse(
                description="Payment not found",
                examples=[
                    OpenApiExample(
                        "Error",
                        value={
                            "status": "error",
                            "messDev": "Payment not found",
                            "messUser": "Payment not found",
                            "data": None
                        }
                    )
                ]
            )
        }
    )
    def audit_history(self, request, pk=None):
        """
        Get the audit history of a payment.
        """
        payment = self.payment_service.get_payment(pk)
        if not payment:
            return Response({
                "status": "error",
                "messDev": "Payment not found",
                "messUser": "Payment not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        history = self.payment_service.get_payment_audit_history(pk)
        return Response(history)