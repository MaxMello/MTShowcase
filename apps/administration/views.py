from MTShowcase import names as _names

from apps.administration.utils import mail
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from apps.user.models import User
from apps.project.models import Project, ProjectSupervisor
from MTShowcase import settings


class AdminView(TemplateView):
    template_name = 'adminpage/admin.html'
    names = _names  # available through view.names in template
    enter_allowed = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = get_object_or_404(User, pk=request.user.id)
            if user.type == User.PROF or user.type == User.ADMIN:
                self.enter_allowed = True
        return super(AdminView, self).dispatch(request, *args, **kwargs)


class InviteUserView(View):
    def post(self, request, *args, **kwargs):
        # Username
        # User´s Email (vorgeprueft)
        # Projekt Name
        # Person, die invited hat
        username = 'Max Mustermann'
        inviter = 'Dirk Mustermann'
        email = ''
        project_name = ''
        context = {'name': username,
                   'inviter': inviter,
                   'site': settings.SITE,
                   'project_name': project_name,
                   'domain': settings.DOMAIN}

        mail('administration/email/user_invite_subject.txt',
             'administration/email/user_invite_mail.txt',
             context, email)


class ProjectListView(ListView):
    model = ProjectSupervisor

    def get_queryset(self):
        pids = ProjectSupervisor.objects.filter(supervisor=self.request.user).values_list('project__pk', flat=True)
        print(ProjectSupervisor.objects.filter(project__projectsupervisor__supervisor_id=1).select_related('project').query)

        return Project.objects.filter(pk__in=pids).order_by('upload_date')
