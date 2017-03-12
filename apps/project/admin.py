from django.contrib import admin
from .models import *

admin.site.register(ProjectSocial)
admin.site.register(ProjectMember)
admin.site.register(ProjectSupervisor)
admin.site.register(ProjectMemberResponsibility)
admin.site.register(ProjectTag)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag)
admin.site.register(Subject)
admin.site.register(DegreeProgram)
admin.site.register(ProjectEditor)
