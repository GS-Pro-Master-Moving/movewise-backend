# api/user/controllers/PasswordResetConfirm.py

from django.shortcuts import render
from django.views import View
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class PasswordResetConfirmView(View):
    
    """
    GET: Renders the password reset form
    POST: Validates the token, updates the password, and marks the token as expired (automatically)
    """

    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')

        # If data is missing, we send a flag to the template
        if not uidb64 or not token:
            return render(request, 'reset_password.html', {
                'no_permission': True,
                'message': "Oops, you don't have permission to access this page."
            })

        return render(request, 'reset_password.html', {
            'uid': uidb64,
            'token': token
        })

    def post(self, request):
        uidb64 = request.POST.get('uid')
        token = request.POST.get('token')
        new_password = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        context = {'uid': uidb64, 'token': token}

        # 1) Validate that the passwords match
        if not new_password or new_password != confirm:
            context['error'] = "Passwords do not match."
            return render(request, 'reset_password.html', context)

        # 2) Decode the UID and get the user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            context['error'] = "Invalid link."
            return render(request, 'reset_password.html', context)

        # 3) Verify the token's validity
        token_gen = PasswordResetTokenGenerator()
        if not token_gen.check_token(user, token):
            context['error'] = "The link has expired or is invalid."
            return render(request, 'reset_password.html', context)

        # 4) Change the password and save
        user.set_password(new_password)
        user.save()

        # 5) The token becomes expired automatically after password change
        context['success'] = "Your password has been successfully changed."
        return render(request, 'reset_password.html', context)
