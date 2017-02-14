import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from MTShowcase import names as _names
from apps.project.models import Project, ProjectSupervisor
from apps.user.models import User
from . import mixins


class InternalUploadView(TemplateView):
    template_name = 'administration/internal_upload.html'
    names = _names  # available through view.names in template
    enter_allowed = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = get_object_or_404(User, pk=request.user.id)
            if user.type == User.PROF or user.type == User.ADMIN:
                self.enter_allowed = True
        return super(InternalUploadView, self).dispatch(request, *args, **kwargs)


class ProfInterfaceView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_master.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context={
                'projects': self.get_projects_for_supervisor(),
                'view': self
            }
        )

    def get_projects_for_supervisor(self):
        user_with_admin_rights = self.request.user.get_lib_user()
        return Project.objects.filter(
            Q(approval_state=Project.REVIEW_STATE) | Q(approval_state=Project.REVISION_STATE),
            projectsupervisor__supervisor=user_with_admin_rights
        ).order_by('upload_date')


class StudentOrganisationView(mixins.ProfAdminPermissionMixin, TemplateView):
    template_name = 'administration/prof_interface_students_content.html'


class ApprovalContentView(ProfInterfaceView):
    template_name = 'administration/prof_interface_approval_content.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps({"text": render_to_string(self.template_name, self.get_projects_for_supervisor())}),
            content_type="application/json"
        )
