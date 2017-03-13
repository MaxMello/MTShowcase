import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, View

from MTShowcase import settings
from apps.project.models import ProjectMember, ProjectEditor, ProjectMemberResponsibility
from apps.user.models import UserSocial
from .forms import RegistrationForm, LoginForm
from .models import RegistrationProfile, AuthEmailUser


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        result = {}
        form = self.form_class(data=request.POST)

        if form.is_valid():
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

                # user authentication using the custom email backend
                login(request, user)

                if request.is_ajax():
                    result = {'success': True}
                else:
                    return super(LoginView, self).form_valid(form)  # non-ajax
        else:
            if request.is_ajax():
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
        form = self.form_class(data=request.POST)

        if form.is_valid():
            # build new user from form after validation
            RegistrationProfile.objects.create_inactive_user(form)

            result = {'success': True,
                      'message':
                          "Registrierung erfolgreich. Ein Aktivierungslink wurde an deine Email ({}) gesendet"
                              .format(form.cleaned_data['email'])}

            if request.is_ajax():
                return HttpResponse(json.dumps(result), content_type="application/json")

            else:
                return super(RegisterView, self).form_valid(form)
        else:
            if request.is_ajax():
                ctx = {'form': form}
                form_html = render_to_string('authentication/register_form.html', context=ctx, request=request)
                result = {'success': False, 'form_html': form_html}

            else:
                return super(RegisterView, self).form_invalid(form)
        return HttpResponse(json.dumps(result), content_type="application/json")

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            ctx = {'form': self.form_class}
            form_html = render_to_string('authentication/register_form.html', context=ctx, request=request)
            result = {'form_html': form_html}
            return HttpResponse(json.dumps(result), content_type="application/json")

        else:
            return super(RegisterView, self).get(request, *args, **kwargs)


class ActivationView(TemplateView):
    template_name = 'authentication/activate.html'

    def get(self, request, *args, **kwargs):
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
        activation_key = kwargs.get('activation_key')
        # this will return the "normal" user, not the auth_user
        return RegistrationProfile.objects.activate_user(activation_key)

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Clear all project contributions
        # Clear User and Auth_user
        user = request.user.get_lib_user()
        contributions = ProjectMember.objects.filter(member=user).values_list("id")
        UserSocial.objects.filter(user=user).delete()
        ProjectEditor.objects.filter(editor=user).delete()
        ProjectMemberResponsibility.objects.filter(project_member_id__in=contributions).delete()
        ProjectMember.objects.filter(member=user).delete()
        user_id = request.user.id
        logout(request)
        AuthEmailUser.objects.get(pk=user_id).delete()
        return redirect(reverse_lazy('home'))
