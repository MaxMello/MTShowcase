from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView

from MTShowcase import names as _names
from apps.project.models import Project
from . import mixins


class InternalUploadView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/internal_upload.html'
    names = _names  # available through view.names in template


class ProfInterfaceView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_master.html'

    def get_context_data(self, **kwargs):
        return {
            'projects': self.get_projects_for_supervisor(),
            'view': self
        }

    def get_projects_for_supervisor(self):
        user_with_admin_rights = self.request.user.get_lib_user()
        return Project.objects.filter(
            Q(approval_state=Project.REVIEW_STATE) | Q(approval_state=Project.REVISION_STATE),
            projectsupervisor__supervisor=user_with_admin_rights
        ).order_by('upload_date')


class StudentOrganisationView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_students_content.html'


class ApprovalContentView(mixins.JSONResponseMixin, ProfInterfaceView):
    template_name = 'administration/prof_interface_approval_content.html'

    def get(self, request, *args, **kwargs):
        return self.render_json_response(
            {"text": render_to_string(self.template_name, self.get_context_data())}
        )
