import json

from MTShowcase import names as ns

from apps.authentication.models import AuthEmailUser
from apps.user.forms import MyPasswordChangeForm, AccountUserForm, UserForm, ProjectPrivacyForm, ShowClearNameForm, \
    UserSocialForm, UserSocialEditForm
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse_lazy
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import FormView, UpdateView
from django.views.generic.base import TemplateView
from apps.project.models import Project, ProjectMember, ProjectMemberResponsibility
from apps.user.models import User, UserSocial
from MTShowcase import names


class UserProfileView(TemplateView):
    template_name = 'user/user.html'

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(unique_name=self.kwargs['unique_name']).get()
        user_projects = ProjectMember.objects.filter(member=user).values_list('project__pk', flat=True)
        projects = Project.objects.filter(id__in=user_projects)
        socials = UserSocial.objects.filter(user=user)
        user_skills = ProjectMemberResponsibility.get_skills_for_user(user)
        for social in user.socials.all():
            print(social)
        context = {'user': user, 'projects': projects, 'names': names, 'usersocials': socials, 'userskills': user_skills}
        http_response = render(request, template_name=self.template_name, context=context)
        return http_response


class SettingsView(TemplateView):
    template_name = 'settings/settings.html'
    names = ns


class SettingAccountView(UpdateView):
    form_class = AccountUserForm
    second_form_class = UserForm
    model = AuthEmailUser
    template_name = 'settings/account_settings.html'
    success_url = reverse_lazy('settings-account')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(SettingAccountView, self).get_context_data(**kwargs)

        user = User.objects.get(auth_user=self.request.user)
        if not 'form' in context:
            context['form'] = self.form_class(instance=self.request.user)
        if not 'form2' in context:
            context['form2'] = self.second_form_class({'unique_name': user.unique_name}, instance=user)
        context['user_profile'] = user

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.request.user)
        form2 = self.second_form_class(request.POST, request.FILES,
                                       instance=User.objects.get(auth_user=self.request.user))

        if form.is_valid() and form2.is_valid():
            form.save(commit=True)
            form2.save(commit=True)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, form2=form2))


class UserSocialView(TemplateView):
    template_name = 'settings/socials_settings.html'
    form = UserSocialForm
    second_form = UserSocialEditForm
    success_url = reverse_lazy('settings-user-socials')

    def get(self, request, *args, **kwargs):
        user = user = User.objects.get(auth_user=self.request.user)
        socials = UserSocial.objects.filter(user=user).values('id', 'social__icon', 'url')
        print(UserSocial.objects.filter(user=user))

        return render(request, self.template_name,
                      {'usersocials': socials, 'form': self.form(user)})

    def post(self, request, *args, **kwargs):
        user = user = User.objects.get(auth_user=self.request.user)
        socials = UserSocial.objects.filter(user=user).values('id', 'social__icon', 'url')
        if request.is_ajax():
            params = request.POST
            context = {'usersocials': socials}
            us = UserSocial.objects.get(id=params['id'])
            context.update({'form': self.second_form(instance=us)})
            context.update({'socialname': us.social.name, 'id': params['id']})
            form_html = render_to_string('settings/socials_edit_form.html', context=context, request=request)
            result = {'form_html': form_html}
            return HttpResponse(json.dumps(result), content_type="application/json")
        else:

            if 'add' in request.POST:
                form = self.form(user, request.POST)
                if form.is_valid():
                    url = form.cleaned_data['url']
                    selection = form.cleaned_data['social_list']

                    # create and save the new usersocial record
                    new_user_social = UserSocial()
                    new_user_social.user = user
                    new_user_social.social = selection
                    new_user_social.url = url
                    new_user_social.save()

            elif 'update' in request.POST:
                id = request.POST['id-user-social']
                obj = UserSocial.objects.get(id=id)
                form = self.second_form(request.POST, instance=obj)
                if form.is_valid():
                    obj.url = form.cleaned_data['url']
                    obj.save()
            elif 'delete' in request.POST:
                id = request.POST['id-user-social']
                obj = UserSocial.objects.get(id=id)
                obj.delete()
            else:
                return HttpResponseBadRequest(request)

            return HttpResponseRedirect(self.success_url)


class PrivacyView(TemplateView):
    template_name = 'settings/privacy_settings.html'
    user_clearnameform = ShowClearNameForm
    user = None
    obj_list = None

    def dispatch(self, request, *args, **kwargs):
        self.user = User.objects.filter(auth_user=request.user)
        self.obj_list = ProjectMember.objects.filter(member=User.objects.get(auth_user=self.request.user))

        return super(PrivacyView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print("#----------# GET FORMSET#-----------#")
        print("Anzahl Privacy Projekte " + str(ProjectMember.objects.filter(member=self.user).count()))

        ProjectMemberFormset = modelformset_factory(ProjectMember, form=ProjectPrivacyForm, extra=0)
        formset = ProjectMemberFormset(queryset=ProjectMember.objects.filter(member=self.user))

        # user clear name form
        userform = self.user_clearnameform(instance=self.user.first())
        return render(request, self.template_name,
                      {'object_list': zip(formset, self.obj_list),
                       'empty_list': len(list(zip(formset, self.obj_list))) > 0,
                       'formset': formset,
                       'userform': userform})

    def post(self, request, *args, **kwargs):
        print("#----------# POST FORMSET#-----------#")
        ProjectMemberFormset = modelformset_factory(ProjectMember, form=ProjectPrivacyForm, extra=0)
        formset = ProjectMemberFormset(request.POST, queryset=ProjectMember.objects.filter(member=self.user))
        userform = self.user_clearnameform(request.POST, instance=self.user.first())
        if formset.is_valid() and userform.is_valid():
            formset.save()
            userform.save()

        return render(request, self.template_name,
                      {'object_list': zip(formset, self.obj_list),
                       'formset': formset,
                       'userform': userform,
                       'empty_list': len(list(zip(formset, self.obj_list))) > 0})


class SettingPasswordChangeView(FormView):
    """View handle password change.

    After change the user will NOT be logged out.
    update_session_auth_hash() -> Updating the password
    logs out all other sessions for the user except the current one

    """
    form_class = MyPasswordChangeForm
    template_name = 'settings/password_change_settings.html'
    success_url = reverse_lazy('password-change-done')

    def dispatch(self, request, *args, **kwargs):
        return password_change(request,
                               password_change_form=self.form_class,
                               template_name=self.template_name,
                               post_change_redirect=self.success_url)


class PasswordChangeDoneView(TemplateView):
    template_name = 'settings/password_change_done.html'


class ProjectListView(TemplateView):
    template_name = 'user/projectlist.html'
    names = ns
