import json

from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, View

from MTShowcase import settings
from .forms import RegistrationForm, LoginForm
from .models import RegistrationProfile


# print("#--#--------" + VALUE + "--------#--#")

class LoginView(FormView):
    form_class = LoginForm
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "LOGIN-FORM POSTED" + "--------#--#")
        result = {}
        form = self.form_class(data=request.POST)

        if form.is_valid():
            if settings.AUTH_DEBUG:
                print("#--#--------" + "LOGIN-FORM VALID" + "--------#--#")
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            user = authenticate(email=email, password=password)
            if user is not None:
                if remember_me:
                    expire = 6 * 30 * 24 * 60 * 60  # six month in seconds
                    self.request.session.set_expiry(expire)
                else:
                    self.request.session.set_expiry(0)  # at browser close

                login(request, user)
                if request.is_ajax():
                    result = {'success': True}
                else:
                    return super(LoginView, self).form_valid(form)  # non-ajax
        else:
            if request.is_ajax():
                if settings.AUTH_DEBUG:
                    print("#--#--------" + "LOGIN AJAX ERRORS" + "--------#--#")
                ctx = {}
                ctx.update({'form': form})
                form_html = render_to_string('authentication/login_form.html', context=ctx, request=request)
                result = {'success': False, 'form_html': form_html}
            else:
                return super(LoginView, self).form_invalid(form)  # non-ajax
        return HttpResponse(json.dumps(result), content_type="application/json")


class RegisterView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy('activation_complete')
    template_name = 'authentication/signup.html'

    def post(self, request, *args, **kwargs):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "SIGNUP-FORM POSTED" + "--------#--#")
        form = self.form_class(data=request.POST)

        if form.is_valid():
            if settings.AUTH_DEBUG:
                print("#--#--------" + "SIGNUP-FORM VALID" + "--------#--#")
            # build new user from form after validation
            RegistrationProfile.objects.create_inactive_user(form)

            result = {'success': True,
                      'message': "Registrierung erfolgreich. Ein Aktivierungslink wurde an deine Email gesendet"}

            if request.is_ajax():
                return HttpResponse(json.dumps(result), content_type="application/json")
            else:
                return super(RegisterView, self).form_valid(form)
        else:
            if request.is_ajax():
                if settings.AUTH_DEBUG:
                    print("#--#--------" + "SIGNUP AJAX ERRORS" + "--------#--#")
                ctx = {'form': form}
                form_html = render_to_string('authentication/register_form.html', context=ctx, request=request)
                result = {'success': False, 'form_html': form_html}
            else:
                return super(RegisterView, self).form_invalid(form)
        return HttpResponse(json.dumps(result), content_type="application/json")

    def get(self, request, *args, **kwargs):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "SIGNUP-GET" + "--------#--#")
        if request.is_ajax():
            if settings.AUTH_DEBUG:
                print("#--#--------" + "REGISTER GET AJAX FORM RESPONSE" + "--------#--#")
            ctx = {'form': self.form_class}
            form_html = render_to_string('authentication/register_form.html', context=ctx, request=request)
            result = {'form_html': form_html}
            return HttpResponse(json.dumps(result), content_type="application/json")
        else:
            return super(RegisterView, self).get(request, *args, **kwargs)


class ActivationView(TemplateView):
    template_name = 'authentication/activate.html'

    def get(self, request, *args, **kwargs):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "ABOUT TO ACTIVATE" + "--------#--#")
        activated_user = self.activate(*args, **kwargs)

        if activated_user:
            success_url = self.get_success_url(activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return redirect('/')

    def activate(self, *args, **kwargs):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "TEST ACTIVATION KEY" + "--------#--#")
        activation_key = kwargs.get('activation_key')
        # this will return the "normal" user, not the auth_user
        activated_user = RegistrationProfile.objects.activate_user(
            activation_key
        )
        return activated_user

    # "DOC": Determine the URL to redirect to when the form is successfully validated.
    # Returns success_url by default.
    def get_success_url(self, user):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "DETERMINE REGISTER COMPLETE URL" + "--------#--#")
        return ('registration_activation_complete', (), {})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # simply logout on get
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')
