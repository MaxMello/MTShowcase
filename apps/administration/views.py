import json

from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView

from MTShowcase import names as _names
from apps.project.models import Project, DegreeProgram
from . import mixins


class InternalUploadView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/internal_upload.html'
    names = _names  # available through view.names in template


class ProfInterfaceView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_master.html'

    def get_context_data(self, **kwargs):
        return {
            'projects': self.get_projects_for_supervisor(),
            'select_json': self.build_select_json(),
            'degree_programs': DegreeProgram.objects.all(),
            'year_choices': Project.YEAR_CHOICES,
            'semester_choices': Project.SEMESTER,
            'view': self
        }

    def get_projects_for_supervisor(self):
        user_with_admin_rights = self.request.user.get_lib_user()
        return Project.objects.filter(
            projectsupervisor__supervisor=user_with_admin_rights
        ).filter(
            Q(approval_state=Project.REVIEW_STATE) | Q(approval_state=Project.REVISION_STATE)
        ).order_by('upload_date')

    @staticmethod
    def build_select_json():
        result = {}
        for degree_program in DegreeProgram.objects.all():
            result.update({degree_program.name: []})
            for subject in degree_program.subjects():
                result[degree_program.name].append(subject.name)
        return result


class StudentOrganisationView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_students_content.html'


class ApprovalContentView(mixins.JSONResponseMixin, ProfInterfaceView):
    template_name = 'administration/prof_interface_approval_content.html'

    def get(self, request, *args, **kwargs):
        return self.render_json_response(
            {"text": render_to_string(self.template_name, self.get_context_data())}
        )


class SupervisorProjectsView(mixins.JSONResponseMixin, ProfInterfaceView):
    template_name = 'administration/prof_interface_projects_content.html'

    def get(self, request, *args, **kwargs):
        return self.render_json_response(
            {"text": render_to_string(self.template_name, self.get_context_data())}
        )

    def get_context_data(self, **kwargs):
        user_with_admin_rights = self.request.user.get_lib_user()
        projects = Project.objects.filter(
            projectsupervisor__supervisor=user_with_admin_rights
        ).filter(
            approval_state=Project.APPROVED_STATE
        ).order_by('upload_date DESC')

        return {'projects': projects}


class ProfInterfaceSearchView(mixins.JSONResponseMixin, mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_projects_content.html'
    sort_order = "-"

    def post(self, request, *args, **kwargs):
        projects = {}
        if request.POST:
            params = json.loads(request.POST.get('params'))
            should_sort_desc = params['sort_order_desc']
            self.sort_order = "-" if should_sort_desc else ""
            projects = self.apply_search(params)

        return self.render_json_response(
            {"text": render_to_string(self.template_name, {'projects': projects})}
        )

    def apply_search(self, params_dict):
        user_with_admin_rights = self.request.user.get_lib_user()
        project_qs = Project.objects.filter(
            projectsupervisor__supervisor=user_with_admin_rights
        ).filter(
            approval_state=Project.APPROVED_STATE
        )

        if params_dict:
            if params_dict['degree_select'] and not params_dict['degree_select'] == 'all':
                project_qs.filter(
                    degree_program__name=params_dict['degree_select']
                )
            if params_dict['subject_select'] and not params_dict['subject_select'] == 'all':
                project_qs.filter(
                    subject__name=params_dict['subject_select']
                )
            if params_dict['year_select'] and not params_dict['year_select'] == 'all':
                project_qs.filter(
                    Q(year_from=params_dict['year_select']) |
                    Q(year_to=params_dict['year_select'])
                )
            if params_dict['semester_select'] and not params_dict['semester_select'] == 'all':
                project_qs.filter(
                    semester=params_dict['semester_select']
                )

        return project_qs.order_by(
            '{}upload_date'.format(self.sort_order)
        )
