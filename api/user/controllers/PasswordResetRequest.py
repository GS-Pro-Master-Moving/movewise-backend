# api/views/password_reset.py

import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.core.mail import send_mail
from django.conf import settings

from api.person.models import Person
from api.user.models import User

logger = logging.getLogger(__name__)

class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request password reset",
        description="Sends a secure recovery link to the provided email if it exists.",
        request={"type": "object", "properties": {"email": {"type": "string"}}},
        examples=[
            OpenApiExample(
                "Request",
                value={"email": "user@outlook.com"},
                request_only=True
            ),
            OpenApiExample(
                "Response",
                value={"detail": "If that email exists, you will receive instructions via email."},
                response_only=True
            ),
        ],
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}}
    )
    def post(self, request):
        try:
            email = request.data.get("email", "").strip().lower()
            response_msg = {
                "detail": "If that email exists, you will receive instructions via email."
            }

            if not email:
                return Response(
                    {"detail": "The email field is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Verificar tanto Person como User en un solo bloque
                person = Person.objects.get(email=email)
                user = User.objects.get(person=person)
            except (Person.DoesNotExist, User.DoesNotExist):
                print(f"Correo o usuario no encontrado: {email}")
                return Response(response_msg, status=status.HTTP_200_OK)

            # Generar token y URL
            token = PasswordResetTokenGenerator().make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                f"/user/reset-password-confirm/?uid={uidb64}&token={token}"
            )
            logger.debug("Generated reset URL: %s", reset_url)

            # 4) Preparar asunto y contenido
            subject = "GS PRO MASTER MOVING - Password Reset Request"
            text_content = (
                f"Hello {person.first_name},\n\n"
                "We received a password reset request for your GS PRO MASTER MOVING account.\n\n"
                f"Reset link: {reset_url}\n\n"
                "This link expires in 1 hour.\n"
                "If you didn't request this, please ignore this email.\n\n"
                "The GS PRO MASTER MOVING Team"
            )
            html_content = f"""
            <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Password Reset</title></head>
            <body style="font-family:Arial;background:#f4f4f4;margin:0;padding:0;">
            <table width="100%" style="max-width:600px;margin:auto;background:#fff;border-radius:8px;box-shadow:0 4px 10px rgba(0,0,0,0.1);">
              <tr><td style="background:#1e3a8a;padding:30px;text-align:center;">
                <h1 style="color:#fff;margin:0;">GS PRO MASTER MOVING</h1>
              </td></tr>
              <tr><td style="padding:40px 30px;color:#333;">
                <p>Hello <strong>{person.first_name}</strong>,</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align:center;margin:30px 0;">
                  <a href="{reset_url}" style="background:#1e3a8a;color:#fff;padding:12px 30px;border-radius:5px;text-decoration:none;font-weight:bold;">
                    Reset My Password
                  </a>
                </p>
                <p>If the button doesn't work, paste this link in your browser:</p>
                <p style="background:#f4f4f4;padding:12px;border-radius:4px;word-break:break-all;">
                  <a href="{reset_url}" style="color:#1e3a8a;">{reset_url}</a>
                </p>
                <p>This link expires in <strong>1 hour</strong>.</p>
              </td></tr>
              <tr><td style="background:#f8f8f8;padding:25px;text-align:center;color:#666;font-size:12px;">
                Thank you for choosing GS PRO MASTER MOVING.<br>
                <a href="https://www.gspromaster.com" style="color:#1e3a8a;">www.gspromaster.com</a> |
                <a href="mailto:support@gspromaster.com" style="color:#1e3a8a;">support@gspromaster.com</a>
              </td></tr>
            </table></body></html>
            """
            logger.debug("Prepared email content for %s", email)

            # 5) Enviar con send_mail y capturar errores
            try:
                send_mail(
                    subject=subject,
                    message=text_content,
                    html_message=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")
                return Response(
                    {"detail": "Error sending reset email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Unhandled error in PasswordResetRequest")
            return Response(
                {"detail": "Internal server error.", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )