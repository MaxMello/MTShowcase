from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.ProfInterfaceView.as_view()),
    url(r'^backoffice/', admin.site.urls),
    url(r'^internal_upload/', views.InternalUploadView.as_view(), name="internal_upload"),

    url(r'^professor/$', views.ProfInterfaceView.as_view(), name='prof_interface'),
    url(r'^projects/$', views.SupervisorProjectsView.as_view(), name='prof_projects'),

    url(r'^approval_content/$', views.ApprovalContentView.as_view(), name='approval_content'),
    url(r'^prof_search', views.ProfInterfaceSearchView.as_view(), name='prof_search'),
    url(r'^project_options_panel/$', views.ProjectOptionsView.as_view(), name='project_options')
]
