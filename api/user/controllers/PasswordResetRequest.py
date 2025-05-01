from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.person.models import Person
from api.user.models import User
from django.conf import settings

class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request password reset",
        description="Sends a secure recovery link to the provided email if it exists.",
        request={"type": "object", "properties": {"email": {"type": "string"}}},
        examples=[OpenApiExample(
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
        email = request.data.get("email", "").strip()
        response_msg = {
            "detail": "If that email exists, you will receive instructions via email."
        }

        if not email:
            return Response({"detail": "The email field is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1) Check if a Person with that email exists
            person = Person.objects.get(email=email)
            # 2) Check if a User is associated with that Person
            user = User.objects.get(person=person)
        except (Person.DoesNotExist, User.DoesNotExist):
            # Do not reveal which one failed; return 200 anyway
            return Response(response_msg, status=status.HTTP_200_OK)

        # 3) Generate unique token and UID
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # 4) Build password reset URL using the request object to get the domain dynamically
        reset_url = request.build_absolute_uri(f"/user/reset-password-confirm/?uid={uidb64}&token={token}")

        # 5) Send email with plain text + HTML
        subject = "Reset your password"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        text_content = (
            f"Hi {person.first_name},\n\n"
            "Someone (hopefully you) requested a password reset for your account.\n"
            f"Click the link below to reset it:\n{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email.\n"
        )
        html_content = f"""
            <p>Hi {person.first_name},</p>
            <p>To reset your password, click the following link:</p>
            <p><a href="{reset_url}">Reset password</a></p>
            <p>If you did not request this, you can ignore this message.</p>
            <hr>
            <p style="font-size:0.8em;color:gray;">
              This link expires in 1 hour and can only be used once.
            </p>
        """

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_msg.attach_alternative(html_content, "text/html")
        # Anti-spam headers
        email_msg.extra_headers = {
            "X-Priority": "1",
            "Reply-To": from_email,
        }
        email_msg.send(fail_silently=False)

        return Response(response_msg, status=status.HTTP_200_OK)
