from django.shortcuts import render
from django.views import View
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
User = get_user_model()

class PasswordResetConfirmView(View):
    """
    GET: Renders the password reset form
    POST: Validates the token, updates the password, and marks the token as expired
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

        # Validar el token antes de mostrar el formulario
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            token_gen = PasswordResetTokenGenerator()
            
            if not token_gen.check_token(user, token):
                return render(request, 'reset_password.html', {
                    'no_permission': True,
                    'message': "The password reset link has expired or is invalid."
                })
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'reset_password.html', {
                'no_permission': True,
                'message': "The password reset link is invalid."
            })

        return render(request, 'reset_password.html', {
            'uid': uidb64,
            'token': token
        })

    def post(self, request):
        email = request.POST.get("email", "").strip().lower()  
        uidb64 = request.POST.get('uid')
        token = request.POST.get('token')
        new_password = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        context = {'uid': uidb64, 'token': token}

        if not new_password or new_password != confirm:
            context['error'] = "Las contraseñas no coinciden."
            return render(request, 'reset_password.html', context)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            context['error'] = "Enlace inválido."
            return render(request, 'reset_password.html', context)

        token_gen = PasswordResetTokenGenerator()
        if not token_gen.check_token(user, token):
            context['no_permission'] = True
            context['message'] = "El enlace ha expirado o es inválido."
            return render(request, 'reset_password.html', context)

        user.set_password(new_password)
        user.save()

        return render(request, 'reset_password.html', {
            'success': "Contraseña actualizada correctamente.",
            'completed': True
        })