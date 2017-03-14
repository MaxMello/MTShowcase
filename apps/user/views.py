import json
from io import BytesIO

from PIL import Image
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile

from MTShowcase import names as ns

from apps.authentication.models import AuthEmailUser
from apps.project.forms import ImageFormField
from apps.user.forms import MyPasswordChangeForm, AccountUserForm, UserForm, ProjectPrivacyForm, ShowClearNameForm, \
    UserSocialForm, UserSocialEditForm
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse_lazy
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.views.generic import FormView, UpdateView
from django.views.generic.base import TemplateView
from apps.project.models import Project, ProjectMember, ProjectMemberResponsibility, ProjectEditor
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

        http_response = render(
            request,
            template_name=self.template_name,
            context={
                'user': user,
                'projects': projects,
                'names': names,
                'usersocials': socials,
                'userskills': user_skills
            }
        )
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
        if not ('form' in context):
            context['form'] = self.form_class(instance=self.request.user)
        if not ('form2' in context):
            context['form2'] = self.second_form_class({'unique_name': user.unique_name}, instance=user)
        context['user_profile'] = user

        return context

    def post(self, request, *args, **kwargs):
        print("SETTINGS########")
        print(request.POST)
        print(request.FILES)
        valid = False
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.request.user)
        form2 = self.second_form_class(
            request.POST,
            request.FILES,
            instance=User.objects.get(auth_user=self.request.user)
        )
        image_form = ImageFormField('profile_img', request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            form.save(commit=True)
            form2.save(commit=True)
            valid = True
        if image_form.is_valid():
            valid = True
            if 'crop_data' in request.POST and request.POST['crop_data']:
                crop_data = json.loads(request.POST['crop_data'])
                f = BytesIO()
                try:
                    img = Image.open(image_form.cleaned_data['profile_img'])
                    img_crop = img.crop((
                        int(crop_data["x"]),
                        int(crop_data["y"]),
                        int(crop_data["x"] + crop_data["width"]),
                        int(crop_data["y"] + crop_data["height"]))
                    )
                    img_crop.save(f, format='JPEG')
                    img_crop_file = ContentFile(f.getvalue(), "croppedimage.jpeg")
                    user = User.objects.get(auth_user=self.request.user)
                    user.profile_img = img_crop_file
                    user.save()
                except Exception as e:
                    print("Failed to open and crop image " + str(e))
                finally:
                    f.close()

        return HttpResponse(
            content=json.dumps(
                {'text': render_to_string(
                    'settings/account_settings_form.html',
                    context=self.get_context_data(form=form, form2=form2),
                    request=request
                ), 'valid': valid}
            ),
            content_type="application/json"
        )


class UserSocialView(TemplateView):
    template_name = 'settings/socials_settings.html'
    form = UserSocialForm
    second_form = UserSocialEditForm
    success_url = reverse_lazy('settings-user-socials')

    def get(self, request, *args, **kwargs):
        user = User.objects.get(auth_user=self.request.user)
        socials = UserSocial.objects.filter(user=user).values('id', 'social__icon', 'url')

        return render(request, self.template_name, {'usersocials': socials, 'form': self.form(user)})

    def post(self, request, *args, **kwargs):
        user = User.objects.get(auth_user=self.request.user)
        socials = UserSocial.objects.filter(user=user).values('id', 'social__icon', 'url')

        if request.is_ajax():
            params = request.POST
            us = UserSocial.objects.get(id=params['id'])

            context = {'usersocials': socials}
            context.update({'form': self.second_form(instance=us)})
            context.update({'socialname': us.social.name, 'id': params['id']})

            form_html = render_to_string('settings/socials_edit_form.html', context=context, request=request)
            return HttpResponse(json.dumps({'form_html': form_html}), content_type="application/json")

        else:
            if 'add' in request.POST:
                form = self.form(user, request.POST)
                if form.is_valid():
                    url = form.cleaned_data['url']
                    selection = form.cleaned_data['social_list']

                    new_user_social = UserSocial()
                    new_user_social.user = user
                    new_user_social.social = selection
                    new_user_social.url = url
                    new_user_social.save()

            elif 'update' in request.POST:
                user_social_id = request.POST['id-user-social']
                user_social_entry = UserSocial.objects.get(id=user_social_id)
                form = self.second_form(request.POST, instance=user_social_entry)
                if form.is_valid():
                    user_social_entry.url = form.cleaned_data['url']
                    user_social_entry.save()

            elif 'delete' in request.POST:
                user_social_id = request.POST['id-user-social']
                user_social_entry = UserSocial.objects.get(id=user_social_id)
                user_social_entry.delete()

            else:
                return HttpResponseBadRequest(request)

            return HttpResponseRedirect(self.success_url)


class PrivacyView(TemplateView):
    template_name = 'settings/privacy_settings.html'
    user_clearnameform = ShowClearNameForm
    user = None
    user_projects = None

    def dispatch(self, request, *args, **kwargs):
        self.user = User.objects.filter(auth_user=request.user)
        self.user_projects = ProjectMember.objects.filter(member=User.objects.get(auth_user=self.request.user))

        return super(PrivacyView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # print("Anzahl Privacy Projekte " + str(ProjectMember.objects.filter(member=self.user).count()))

        ProjectMemberFormset = modelformset_factory(ProjectMember, form=ProjectPrivacyForm, extra=0)
        formset = ProjectMemberFormset(queryset=ProjectMember.objects.filter(member=self.user))

        user_show_clearname_form = self.user_clearnameform(instance=self.user.first())
        return render(
            request,
            self.template_name,
            context={
                'object_list': zip(formset, self.user_projects),
                'empty_list': len(list(zip(formset, self.user_projects))) > 0,
                'formset': formset,
                'userform': user_show_clearname_form
            }
        )

    def post(self, request, *args, **kwargs):
        ProjectMemberFormset = modelformset_factory(ProjectMember, form=ProjectPrivacyForm, extra=0)
        formset = ProjectMemberFormset(request.POST, queryset=ProjectMember.objects.filter(member=self.user))
        user_show_clearname_form = self.user_clearnameform(request.POST, instance=self.user.first())

        if formset.is_valid() and user_show_clearname_form.is_valid():
            formset.save()
            user_show_clearname_form.save()

        return render(
            request,
            self.template_name,
            context={
                'object_list': zip(formset, self.user_projects),
                'formset': formset,
                'userform': user_show_clearname_form,
                'empty_list': len(list(zip(formset, self.user_projects))) > 0
            }
        )


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
        return password_change(
            request,
            password_change_form=self.form_class,
            template_name=self.template_name,
            post_change_redirect=self.success_url
        )


class PasswordChangeDoneView(TemplateView):
    template_name = 'settings/password_change_done.html'


class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = 'user/projectlist.html'

    def get_context_data(self, **kwargs):
        return {'drafts': ProjectEditor.objects.filter(editor=self.request.user.get_lib_user())}
