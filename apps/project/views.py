from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import TemplateView
from apps.project.models import *
from MTShowcase import names
from random import randint


class ProjectView(TemplateView):
    template_name = 'project/projectdetails.html'

    def get(self, request, *args, **kwargs):
        project = Project.objects.filter(id=int(self.kwargs['project_id'])).first()
        project.views += 1
        project.save()

        count = Project.objects.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        next_project = Project.objects.all()[random_index]

        member_privacy = ProjectMember.objects.filter(project=project).values_list('display_username', flat=True)
        member_resps = [member.get_responsibilities() for member in ProjectMember.objects.filter(project=project).order_by("member__id")]
        project_socials = ProjectSocial.objects.filter(project=project)
        context = {'entries': zip(project.members.all().order_by("id"), member_privacy, member_resps), 'project': project, 'names': names,
                   'next': next_project, 'project_socials': project_socials}
        print(context)
        return render(request, template_name=self.template_name, context=context)


class UploadView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'upload/projectupload.html'

    def get(self, request, *args, **kwargs):
        degree_programs = DegreeProgram.objects.all()
        subjects = Subject.objects.all()
        year_choices = reversed([r for r in range(1980, datetime.date.today().year + 1)])
        context = {'names': names, 'degree_programs': degree_programs, 'subjects': subjects, 'year_choices': year_choices}

        project_id = self.kwargs.get('project_id')
        if project_id:
            project = Project.objects.filter(id=int(project_id)).first()
            context['project'] = project
        return render(request, template_name=self.template_name, context=context)
