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
        subject = "GS PRO MASTER MOVING - Password Reset Request"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        
        # Plain text version for email clients that don't support HTML
        text_content = (
            f"Hello {person.first_name},\n\n"
            "We received a request to reset your password for your GS PRO MASTER MOVING account.\n\n"
            f"To reset your password, please click on the following link or paste it into your browser:\n{reset_url}\n\n"
            "This link will expire in 1 hour for security reasons.\n\n"
            "If you did not request this password reset, please ignore this email and your password will remain unchanged.\n\n"
            "Thank you,\n"
            "The GS PRO MASTER MOVING Team\n"
            "For assistance: support@gspromaster.com"
        )
        
        # HTML version with styling
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
            <table cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <!-- Header -->
                <tr>
                    <td style="background-color: #1e3a8a; padding: 30px 0; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; padding: 0; font-size: 28px;">GS PRO MASTER MOVING</h1>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <p style="margin-top: 0; font-size: 16px; color: #333333;">Hello <strong>{person.first_name}</strong>,</p>
                        
                        <p style="font-size: 16px; color: #333333; line-height: 1.5;">We received a request to reset the password for your GS PRO MASTER MOVING account. To reset your password, please click on the button below:</p>
                        
                        <div style="text-align: center; margin: 35px 0;">
                            <a href="{reset_url}" style="background-color: #1e3a8a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; font-size: 16px;">Reset My Password</a>
                        </div>
                        
                        <p style="font-size: 16px; color: #333333; line-height: 1.5;">If the button doesn't work, please copy and paste the following link into your browser:</p>
                        
                        <p style="background-color: #f4f4f4; padding: 12px; border-radius: 4px; font-size: 14px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all;">
                            <a href="{reset_url}" style="color: #1e3a8a; text-decoration: none;">{reset_url}</a>
                        </p>
                        
                        <p style="font-size: 16px; color: #333333; line-height: 1.5;">This link will expire in <strong>1 hour</strong> for security reasons.</p>
                        
                        <p style="font-size: 16px; color: #333333; line-height: 1.5;">If you did not request a password reset, please ignore this email or contact our support team if you have concerns.</p>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f8f8; padding: 25px 30px; border-top: 1px solid #eeeeee;">
                        <p style="margin: 0; font-size: 14px; color: #666666; line-height: 1.5; text-align: center;">
                            Thank you for choosing GS PRO MASTER MOVING.<br>
                            If you need assistance, please contact our support team.
                        </p>
                        
                        <div style="margin-top: 20px; text-align: center;">
                            <a href="https://www.gspromaster.com" style="color: #1e3a8a; text-decoration: none; font-size: 14px;">www.gspromaster.com</a>
                            <span style="margin: 0 10px; color: #dddddd;">|</span>
                            <a href="mailto:support@gspromaster.com" style="color: #1e3a8a; text-decoration: none; font-size: 14px;">support@gspromaster.com</a>
                        </div>
                        
                        <p style="margin-top: 25px; font-size: 12px; color: #999999; text-align: center;">
                            This email was sent to you because a password reset was requested for your account.<br>
                            If you didn't request this action, you can safely ignore this email.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_msg.attach_alternative(html_content, "text/html")
        # Anti-spam headers
        email_msg.extra_headers = {
            "X-Priority": "1",
            "Reply-To": from_email,
            "X-Mailer": "GS PRO MASTER MOVING System"
        }
        email_msg.send(fail_silently=False)

        return Response(response_msg, status=status.HTTP_200_OK)