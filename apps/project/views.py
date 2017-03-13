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
from apps.project.forms import ImageFormField, AudioFileField, VideoFileField
from apps.project.image_crop import crop_image_and_save
from apps.project.models import *
from apps.project.validators import UrlToSocialMapper, url_validator, is_provider_url, validate_empty

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


def get_iframe_from_oembed_or_none(url, provider_name):
    if provider_name is None:
        return None

    from urllib.parse import quote

    if provider_name == 'vimeo.com':
        embed_base_url = "https://{}/api/oembed.json?url={}"
        embed_request_url = embed_base_url.format(provider_name, quote(url))
    elif provider_name == 'youtube.com':
        embed_base_url = "https://www.youtube.com/oembed?url={}&format=json"
        embed_request_url = embed_base_url.format(quote(url))
    elif provider_name == 'soundcloud.com':
        embed_base_url = "https://soundcloud.com/oembed?format=json&url={}"
        embed_request_url = embed_base_url.format(quote(url))
    else:
        return None

    r = requests.get(embed_request_url)
    if r.status_code == 200:
        return r.json()['html']
    else:
        return None


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

        if request.POST and request.POST.get('params'):
            project_params = json.loads(request.POST.get('params'))
            print(request.POST)
            print(project_params)

            try:
                method = project_params['upload_method']
                heading = project_params['p_heading']
                subheading = project_params['p_subheading']
                description = project_params['p_description']
                degree_program_id = project_params['p_degree_program']
                semesteryear = project_params['p_semesteryear']
                subject_id = project_params['p_subject']
                supervisors_list = project_params['p_supervisors']
                member_resp_list = project_params['p_member_responsibilities']
                project_tags = project_params['p_project_tags']
                project_links = project_params['p_project_links']
                project_contents = project_params['p_contents']
                crop_data = json.loads(request.POST['crop_data']) if 'crop_data' in request.POST else None
            except KeyError as ke:
                print("key error " + str(ke))
                return HttpResponseBadRequest()

            if semesteryear is None or semesteryear[:2] is None or semesteryear[:2] not in [Project.WINTER,
                                                                                            Project.SUMMER]:
                print("wrong semester")
                return HttpResponseBadRequest()

            semester = semesteryear[:2]
            year_from = (semesteryear[2:])
            year_choices = reversed([r for r in range(1980, datetime.date.today().year + 1)])
            if year_from is None or int(year_from) not in year_choices:
                print("bad year input")
                return HttpResponseBadRequest()
            year_to = int(year_from) + 1 if semester == Project.WINTER else year_from

            degree_program = get_object_or_404(DegreeProgram, pk=degree_program_id)
            subject = get_object_or_404(Subject, pk=subject_id)

            if method == 'publish':
                failed1, result1 = validate_empty(heading, "heading", "Der Titel")
                failed2, result2 = validate_empty(subheading, "subheading", "Der Unteritel")
                failed3, result3 = validate_empty(description, "description", "Die Projektbechreibung")
                response = None
                if failed1:
                    response = result1
                elif failed2:
                    response = result2
                elif failed3:
                    response = result3
                if response:
                    return self.render_json_response(response, status=400)

                if not supervisors_list:
                    return self.render_json_response(
                        {"id": "upload-top-right", "msg": "Jedes Projekt braucht einen Betreuer!"}, status=400)

            existing_project = None
            if request.POST and 'project_unique_id' in request.POST:
                print("########## GOT EXISTING #+++++++++++++++++")
                project_id = Project.base64_to_uuid(request.POST.get("project_unique_id"))
                try:
                    existing_project = Project.objects.filter(unique_id=project_id).get()
                except:
                    pass

            if existing_project:
                new_project = existing_project
                new_project.heading = heading
                new_project.subheading = subheading
                new_project.description = description
                new_project.semester = semester
                new_project.year_from = year_from
                new_project.year_to = year_to
                new_project.degree_program = degree_program
                new_project.subject = subject
                new_project.save()
            else:
                new_project = Project.objects.create(
                    # image
                    # image crop
                    heading=heading,
                    subheading=subheading,
                    description=description,
                    semester=semester,
                    year_from=year_from,
                    year_to=year_to,
                    degree_program=degree_program,
                    subject=subject,
                )

            # socials M2M
            try:
                for social_url in project_links:
                    social = UrlToSocialMapper.return_social_from_url_or_none(social_url)
                    if social:
                        ProjectSocial.objects.get_or_create(project=new_project, social=social, url=social_url)

            except (TypeError, AttributeError, Exception):
                return HttpResponseBadRequest()

            # tags M2M
            try:
                for index, tag in enumerate(project_tags):
                    print(tag)
                    if tag_validation_pattern.match(tag):
                        new_tag, created = Tag.objects.get_or_create(value=tag)
                        ProjectTag.objects.create(project=new_project, tag=new_tag, position=index)
            except (TypeError, AttributeError, Exception):
                # TODO: add error msg as form validation error collection and display hints for user
                return HttpResponseBadRequest()

            # members M2M
            try:
                non_empty_keys = {key for key in member_resp_list.keys() if key and key.isdigit()}

                all_students_ids = User.objects.all().values_list("id", flat=True)
                if not all(int(key) in all_students_ids for key in non_empty_keys):
                    print("bad member resp")
                    return HttpResponseBadRequest()
            except (TypeError, AttributeError, Exception):
                return HttpResponseBadRequest()

            for (index, key) in enumerate(non_empty_keys):
                tags = member_resp_list[key]
                user = User.objects.get(pk=key)
                member, created = ProjectMember.objects.get_or_create(member=user, project=new_project)
                for tag in tags:
                    new_tag, created = Tag.objects.get_or_create(value=tag)
                    ProjectMemberResponsibility.objects.create(
                        project_member=member,
                        responsibility=new_tag,
                        position=index
                    )

            # supervisors M2M
            all_supervisors = User.objects.filter(type=User.PROF)
            for supervisor_id in supervisors_list:
                supervisor = User.objects.get(pk=supervisor_id)
                if supervisor is None or supervisor not in all_supervisors:
                    print("supervisor unknown or not accepted")
                    return HttpResponseBadRequest()

                ProjectSupervisor.objects.get_or_create(project=new_project, supervisor=supervisor)

            if request.FILES:
                form = ImageFormField("title_image", request.POST, request.FILES)
                if form.is_valid():
                    print("cleaned: ", form.cleaned_data["title_image"])
                    new_project.project_image = request.FILES["title_image"]
                    new_project.save()

                    f = BytesIO()
                    try:

                        if crop_data:
                            img = Image.open(new_project.project_image.path)
                            img_crop = img.crop((
                                int(crop_data["x"]),
                                int(crop_data["y"]),
                                int(crop_data["x"] + crop_data["width"]),
                                int(crop_data["y"] + crop_data["height"]))
                            )

                            width, height = img_crop.size
                            if width >= 1280 and height >= 720:
                                img_crop = img_crop.resize((1280, 720), Image.ANTIALIAS)

                            img_crop.save(f, quality=95, optimize=True, format='PNG')
                            img_crop_file = ContentFile(f.getvalue(), "croppedimage.png")
                            new_project.project_image_cropped = img_crop_file
                            new_project.save()

                        f = BytesIO()
                        project_img = Image.open(form.cleaned_data["title_image"])
                        project_card_max_width = 500

                        if project_img.size[0] >= 500:
                            wpercent = (project_card_max_width / float(project_img.size[0]))
                            hsize = int((float(project_img.size[1]) * float(wpercent)))

                            img_resized = project_img.resize((project_card_max_width, hsize), Image.ANTIALIAS)
                            img_resized.save(f, quality=95, optimize=True, format='PNG')
                            project_img_file = ContentFile(f.getvalue(), "projectimageresize.png")
                            new_project.project_image = project_img_file
                            new_project.save()
                    except Exception as e:
                        print("-------------------------------------")
                        print("Failed to open and crop image " + str(e))
                        print("-------------------------------------")
                    finally:
                        f.close()

            # variable content building
            project_json_content = []
            old_project_json = new_project.contents

            section_content_list = project_contents['content']
            for key in sorted(section_content_list):  # for all content sections (add-content-areas)
                current_section = {}
                content_section_obj = section_content_list[key]
                content_type = content_section_obj['content_type']
                visibility = content_section_obj['visibility']
                current_section['subheading'] = content_section_obj['subheading']
                current_section['content_type'] = content_type
                current_section['visibility'] = visibility
                current_section['contents'] = []

                for content in content_section_obj['content']:  # single input content inside each content section
                    print("###################################")
                    print(content)
# VIDEO             # +++++++++++++++++++++++++++++++++++++++++++++
                    if content_type == Project.VIDEO:
                        if 'filename' in content:
                            if 'existing' in content['filename']:
                                existing_data = content['filename']['existing']
                                file_url = existing_data['url']
                                original_name = existing_data['original_name']
                                current_section['contents'].append({
                                    "content_type": content_type,
                                    "filename": file_url,
                                    "original_name": original_name,
                                    "text": content['text']
                                })
                            else:
                                field = content['filename']
                                form = VideoFileField(field, request.POST, request.FILES)
                                if form.is_valid():
                                    original_name = form.cleaned_data[field].name
                                    saved_file = UploadVideo.objects.create(file=form.cleaned_data[field])
                                    if saved_file is not None:
                                        try:
                                            current_section['contents'].append({
                                                "content_type": content_type,
                                                "filename": saved_file.file.url,
                                                "original_name": original_name,
                                                "text": content['text']
                                            })
                                        except KeyError as e:
                                            print("error while video labels" + str(e))
                        elif 'url' in content:
                            try:
                                url_validator(content['url'])
                                provider = None
                                if is_provider_url(content['url'], 'vimeo.com'):
                                    provider = 'vimeo.com'
                                    media_host = "VIMEO"
                                elif is_provider_url(content['url'], 'youtube.com'):
                                    provider = 'youtube.com'
                                    media_host = "YOUTUBE"

                                iframe_html = get_iframe_from_oembed_or_none(content['url'], provider)
                                if iframe_html and media_host:
                                    current_section['contents'].append({
                                        "content_type": content_type,
                                        "media_host": media_host,
                                        "url": content['url'],
                                        "i_frame": iframe_html,
                                        "text": content['text']
                                    })
                            except ValidationError as e:
                                print("error vimeo " + str(e))
                                pass
# AUDIO             # +++++++++++++++++++++++++++++++++++++++++++++
                    elif content_type == Project.AUDIO:
                        if 'filename' in content:
                            if 'existing' in content['filename']:
                                existing_data = content['filename']['existing']
                                file_url = existing_data['url']
                                original_name = existing_data['original_name']
                                current_section['contents'].append({
                                    "content_type": content_type,
                                    "filename": file_url,
                                    "original_name": original_name,
                                    "text": content['text']
                                })
                            else:
                                field = content['filename']
                                form = AudioFileField(field, request.POST, request.FILES)
                                if form.is_valid():
                                    original_name = form.cleaned_data[field].name
                                    saved_file = UploadAudio.objects.create(file=form.cleaned_data[field])
                                    if saved_file is not None:
                                        try:
                                            current_section['contents'].append({
                                                "content_type": content_type,
                                                "filename": saved_file.file.url,
                                                "original_name": original_name,
                                                "text": content['text']
                                            })
                                            print(saved_file.file.url)
                                        except KeyError as e:
                                            print("error while audio " + str(e))

                                else:
                                    print(form.errors)

                        elif 'url' in content:
                            try:
                                url_validator(content['url'])
                                iframe_html = None
                                if is_provider_url(content['url'], 'soundcloud.com'):
                                    provider = 'soundcloud.com'
                                    media_host = 'SOUNDCLOUD'
                                    iframe_html = get_iframe_from_oembed_or_none(content['url'], provider)

                                if iframe_html:
                                    current_section['contents'].append({
                                        "content_type": content_type,
                                        "media_host": media_host,
                                        "url": content['url'],
                                        "i_frame": iframe_html,
                                        "text": content['text']
                                    })
                            except ValidationError:
                                pass
# TEXT              # +++++++++++++++++++++++++++++++++++++++++++++
                    elif content_type == Project.TEXT:
                        current_section['contents'].append({
                            'content_type': content_type,
                            'text': content['text']
                        })
# Slideshow         # +++++++++++++++++++++++++++++++++++++++++++++
                    elif content_type == Project.SLIDESHOW:
                        image_urls = []
                        for existing_url in content['existing']:
                            image_urls.append(existing_url)

                        for field_name in content['slideshow']:
                            form = ImageFormField(field_name, request.POST, request.FILES)
                            if form.is_valid():
                                saved_file = UploadImage.objects.create(file=form.cleaned_data[field_name])
                                if saved_file is not None:
                                    image_urls.append(saved_file.file.url)
                            else:
                                print(form.errors)

                        if image_urls:
                            current_section['contents'].append({
                                'content_type': content_type,
                                'images': image_urls
                            })

# IMAGE             # +++++++++++++++++++++++++++++++++++++++++++++
                    elif content_type == Project.IMAGE:
                        if 'filename' in content:
                            crop_data = None
                            saved_file = None
                            if 'crop_data' in content:
                                try:
                                    crop_data = json.loads(content['crop_data'])
                                except Exception as e:
                                    print("could not load crop data ", str(e))
                                    pass

                            if 'existing' in content['filename']:
                                existing_data = content['filename']['existing']
                                file_url = existing_data['url']
                                original_name = existing_data['original_name']
                                if crop_data:
                                    # TODO: test in production
                                    path = UploadImage.objects.get(file=file_url.replace("/media/", "")).file.path
                                    saved_file = crop_image_and_save(path, crop_data)
                                    # delete old image from storage
                                    UploadImage.objects.get(file=file_url.replace("/media/", "")).file.delete()

                                current_section['contents'].append({
                                    "content_type": content_type,
                                    "filename": saved_file.file.url if saved_file else file_url,
                                    "original_name": original_name,
                                    "text": content['text']
                                })

                            else:
                                field_name = content['filename']
                                form = ImageFormField(field_name, request.POST, request.FILES)
                                if form.is_valid():
                                    original_name = form.cleaned_data[field_name].name
                                    if crop_data:
                                        saved_file = crop_image_and_save(form.cleaned_data[field_name], crop_data)
                                    else:
                                        saved_file = UploadImage.objects.create(file=form.cleaned_data[field_name])

                                    current_section['contents'].append({
                                        "content_type": content_type,
                                        "filename": saved_file.file.url,
                                        "original_name": original_name,
                                        "text": content['text']
                                    })

                        elif 'url' in content:
                            try:
                                url_validator(content['url'])
                                current_section['contents'].append({
                                    "content_type": content_type,
                                    "url": content['url'],
                                    "text": content['text']
                                })
                            except ValidationError:
                                pass
                    # +++++++++++++++++++++++++++++++++++++++++++++
                # end for content in section

                project_json_content.append(current_section)

            print("###########################################################################")
            print(project_json_content)
            print("###########################################################################")
            response_data = {
                "redirect": str(reverse_lazy('project', kwargs={'base64_unique_id': new_project.unique_id_base64()})),
            }

            # removes files that are not used any more in this state of the project
            # to clear storage space
            if old_project_json is not None:
                from .clear_files import clear_removed_files
                clear_removed_files(old_project_json, project_json_content)

            new_project.contents = project_json_content
            if method == 'publish':
                new_project.approval_state = Project.REVIEW_STATE
            elif method == 'save':
                print("save")
                response_data = {"save_success": True, }
                if not existing_project:
                    response_data.update({"redirect": str(
                        reverse_lazy('edit-project', kwargs={'base64_unique_id': new_project.unique_id_base64()}))})
            new_project.save()

            ProjectEditor.objects.get_or_create(project=new_project, editor=request.user.get_lib_user())

            return self.render_json_response(response_data)

        return self.render_json_response({})


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
