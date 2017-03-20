import json
import os
from io import BytesIO
from random import randint

import requests
from PIL import Image
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView, View

import apps.administration.mixins as mixins
from MTShowcase import names
from MTShowcase import settings
from apps.administration.mail_utils import mail
from apps.project.content_handler import EmptyFileContentException
from apps.project.forms import ImageFormField, AudioFileField, VideoFileField
from apps.project.image_crop import crop_image_and_save
from apps.project.models import *
from apps.project.providers import EmbedProvider, Youtube, Vimeo, Soundcloud
from apps.project.upload import Uploader, UploaderInitializationException
from apps.project.validators import UrlToSocialMapper, url_validator, validate_empty

char_umlaut_range = '[a-zA-Z\u00c4\u00e4\u00d6\u00f6\u00dc\u00fc\u00df]'
tag_validation_pattern = re.compile(
    '^({}+[\s-])*{}+$'.format(char_umlaut_range, char_umlaut_range))


class ProjectView(TemplateView):
    template_name = 'project/projectdetails.html'

    def get(self, request, *args, **kwargs):
        unique_project_id = Project.base64_to_uuid(self.kwargs.get('base64_unique_id'))
        project = get_object_or_404(Project, unique_id=unique_project_id)

        user = request.user.get_lib_user() if request.user.is_authenticated() else None
        show_release_panel = True if user is not None and user in project.supervisors.all() and project.approval_state != Project.APPROVED_STATE else False

        if project.approval_state != Project.APPROVED_STATE:
            if not show_release_panel:
                if not list(ProjectEditor.objects.filter(project=project, editor=user)):
                    raise Http404()

        project.views += 1
        project.save()

        count = Project.objects.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        next_project = Project.objects.all()[random_index]

        project_socials = ProjectSocial.objects.filter(project=project)
        member_privacy = ProjectMember.objects.filter(project=project).values_list('display_username', flat=True)
        member_resps = [
            member.get_responsibilities()
            for member in ProjectMember.objects.filter(project=project).order_by("member__id")
            ]

        return render(
            request,
            template_name=self.template_name,
            context={
                'entries': zip(project.members.all().order_by("id"), member_privacy, member_resps),
                'project': project,
                'names': names,
                'next': next_project,
                'project_socials': project_socials,
                'show_release_optionpanel': show_release_panel
            }
        )

    def post(self, request, *args, **kwargs):
        unique_project_id = Project.base64_to_uuid(kwargs.get('base64_unique_id'))
        project = get_object_or_404(Project, unique_id=unique_project_id)
        if request.user.is_authenticated() and request.user.get_lib_user() in project.supervisors.all():
            if 'release' in request.POST:
                project_state = Project.APPROVED_STATE

            elif 'revision' in request.POST:
                project_state = Project.REVISION_STATE
                revision_msg = request.POST['revision_message'] if 'revision_message' in request.POST else None
                if revision_msg is not None:

                    context = {
                        'project': project,
                        'revision_comment': revision_msg
                    }
                    subject, html_message = mail(
                        'administration/mails/revision_mail_subject.txt',
                        'administration/mails/revision_mail_content.html',
                        context,
                        commit=False
                    )
                    recipient_list = []
                    for member in project.members.all():
                        recipient_list.append(member.auth_user.email)

                    send_mail(
                        subject,
                        '',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        html_message=html_message,
                        recipient_list=recipient_list,
                        fail_silently=False
                    )

            project.approval_state = project_state
            project.save()
            return redirect(reverse_lazy("prof_interface"))

        else:
            raise PermissionDenied()


class DeleteView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        print("delete action")
        print(request.POST)

        try:
            project_id = Project.base64_to_uuid(request.POST.get("project_unique_id"))
            existing_project = Project.objects.filter(unique_id=project_id).first()
            if existing_project:
                if existing_project.approval_state != Project.EDIT_STATE:
                    raise Exception()
                project_editor = ProjectEditor.objects.filter(
                    editor=request.user.get_lib_user(),
                    project=existing_project
                ).first()

                if project_editor:
                    print("About to delete")
                    # user owns this project we can go on deleting
                    project_editor.project.delete()
        except Exception as e:
            print(str(e))
            return self.render_json_response({}, status=400)

        return self.render_json_response({"redirect": str(reverse_lazy('home'))})


class UploadView(LoginRequiredMixin, mixins.JSONResponseMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'upload/projectupload.html'

    def get(self, request, *args, **kwargs):
        degree_programs = DegreeProgram.objects.all()
        subjects = Subject.objects.all()
        year_choices = reversed([r for r in range(1980, datetime.date.today().year + 1)])
        context = {
            'names': names,
            'degree_programs': degree_programs,
            'subjects': subjects,
            'year_choices': year_choices,
            'users': User.objects.exclude(pk=request.user.id),
            'all_supervisor': User.objects.filter(type=User.PROF)
        }

        unique_project_id = Project.base64_to_uuid(self.kwargs.get('base64_unique_id'))
        if unique_project_id:
            project = get_object_or_404(Project, unique_id=unique_project_id, approval_state=Project.EDIT_STATE)
            context['project'] = project
            context['project_social'] = ProjectSocial.objects.filter(project=project)
            context['member_resp'] = [
                (member, member.get_responsibilities())
                for member in ProjectMember.objects.filter(project=project).order_by("member__id")
                ]
            context['project_supervisors'] = ProjectSupervisor.objects.filter(project=project)
            print(context['member_resp'])

        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        try:
            uploader = Uploader(request)
            if uploader.is_valid():
                print("########## Send success response")
                return self.render_json_response(uploader.response_data())
            else:
                print("########## Send failure response")
                return self.render_json_response(uploader.response_data(), status=400)

        except UploaderInitializationException as e:
            # If an error happens on the initialization step of the uploader instance we got some invalid
            # data from the client so abandon processing
            return self.render_json_response({}, status=400)


def get_subjects_by_degree_program(request, degree_program_id):
    degree_program = DegreeProgram.objects.filter(id=degree_program_id).first()
    if degree_program:
        # print(degree_program.subjects())
        response = [{"id": subject.id, "name": subject.name} for subject in degree_program.subjects()]
        return HttpResponse(json.dumps(response), content_type='application/json')

    else:
        return HttpResponse(json.dumps([]), content_type='application/json')


class MemberChoicesRespJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        user_choice_rendered = render_to_string(
            'upload/member_resp_choices.html',
            {'users': User.objects.exclude(pk=request.user.id)}
        )
        return self.render_json_response({"text": user_choice_rendered})


class SupervisorChoicesJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        return self.render_json_response({
            "text": render_to_string(
                'upload/supervisor_choices.html', {
                    'supervisors': User.objects.filter(type=User.PROF)
                }
            )
        })


class AddContentJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            content_type = kwargs.get('content_type')
            if content_type == 'text':
                template = 'upload/content_text.html'
            elif content_type == 'slideshow':
                template = 'upload/content_slideshow.html'
            elif content_type == 'audio':
                template = 'upload/content_audio.html'
            elif content_type == 'video':
                template = 'upload/content_video.html'
            elif content_type == 'image':
                template = 'upload/content_image.html'
            else:
                return HttpResponseBadRequest()
        except AttributeError:
            return HttpResponseBadRequest()
        else:
            return self.render_json_response({"text": render_to_string(template, request=request)})


class ChooseContentJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        return self.render_json_response({"text": render_to_string('upload/addcontent.html')})


class ChooseContentChoicesJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        return self.render_json_response({"text": render_to_string('upload/addcontentchoice.html')})


class FileInputTemplateJsonResponseView(LoginRequiredMixin, mixins.JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            input_for = kwargs.get('input_for')
            if input_for == 'audiofile':
                template = 'upload/audio_file_input.html'
            elif input_for == 'soundcloud':
                template = 'upload/soundcloud_input.html'
            elif input_for == 'videofile':
                template = 'upload/video_file_input.html'
            elif input_for == 'videolink':
                template = 'upload/video_link_input.html'
            elif input_for == 'imagelink':
                template = 'upload/image_link_input.html'
            elif input_for == 'imagefile':
                template = 'upload/image_file_input.html'
            else:
                return HttpResponseBadRequest()
        except AttributeError:
            return HttpResponseBadRequest()
        else:
            return self.render_json_response({"text": render_to_string(template, request=request)})
