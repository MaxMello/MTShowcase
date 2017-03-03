from random import randint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView, View

from MTShowcase import names
from MTShowcase import settings
from apps.administration.mail_utils import mail
from apps.project.models import *
import apps.administration.mixins as mixins


class ProjectView(TemplateView):
    template_name = 'project/projectdetails.html'

    def get(self, request, *args, **kwargs):
        unique_project_id = Project.base64_to_uuid(self.kwargs.get('base64_unique_id'))
        project = get_object_or_404(Project, unique_id=unique_project_id)

        user = request.user.get_lib_user() if request.user.is_authenticated() else None
        show_release_panel = True if user is not None and user in project.supervisors.all() and project.approval_state != Project.APPROVED_STATE else False

        if project.approval_state != Project.APPROVED_STATE:
            if not show_release_panel:
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
            'year_choices': year_choices
        }

        unique_project_id = Project.base64_to_uuid(self.kwargs.get('base64_unique_id'))
        if unique_project_id:
            project = get_object_or_404(Project, unique_id=unique_project_id)
            context['project'] = project

        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """
        Titel
        Untertitel
        Kurzbeschreibung

        Projektmitglieder (mit Tätigkeiten)
        Betreuer
        Studiengang
        Fach
        Semester

        Tags
        """
        if request.POST and request.POST.get('params'):
            project_params = json.loads(request.POST.get('params'))
            print(project_params)
            try:
                heading = project_params['p_heading']
                subheading = project_params['p_subheading']
                description = project_params['p_description']
                degree_program_id = project_params['p_degree_program']
                semesteryear = project_params['p_semesteryear']
                subject_id = project_params['p_subject']
                supervisors_list = project_params['p_supervisors']
                member_resp_list = project_params['p_member_responsibilities']
            except KeyError:
                print("key error")
                return HttpResponseBadRequest()

            semester = semesteryear[:2]
            if semester is None or semester not in [Project.WINTER, Project.SUMMER]:
                print("wrong semester")
                return HttpResponseBadRequest()

            year_from = (semesteryear[2:])
            year_choices = reversed([r for r in range(1980, datetime.date.today().year + 1)])
            if year_from is None or int(year_from) not in year_choices:
                print("bad year input")
                return HttpResponseBadRequest()
            year_to = int(year_from) + 1 if semester == Project.WINTER else year_from

            degree_program = get_object_or_404(DegreeProgram, pk=degree_program_id)
            subject = get_object_or_404(Subject, pk=subject_id)

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
                approval_state=Project.REVIEW_STATE
            )

            # socials M2M
            # tags M2M

            # members M2M
            non_empty_keys = {key for key in member_resp_list.keys() if key and key.isdigit()}

            all_students_ids = User.objects.filter(type=User.PROF).values_list("id", flat=True)
            if not all(int(key) in all_students_ids for key in non_empty_keys):
                print("bad member resp")
                return HttpResponseBadRequest()

            for (index, key) in enumerate(non_empty_keys):
                tags = member_resp_list[key]
                user = User.objects.get(pk=key)
                member = ProjectMember.objects.create(member=user, project=new_project)
                for tag in tags:
                    new_tag = Tag.objects.create(value=tag)
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

                ProjectSupervisor.objects.create(project=new_project, supervisor=supervisor)

            return self.render_json_response({})
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
