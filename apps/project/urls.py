from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^p/(?P<project_id>[0-9]+)$', views.ProjectView.as_view(), name='project'),
    url(r'^me/project/new/$', views.UploadView.as_view(), name='new-project'),
    url(r'^me/project/(?P<project_id>[0-9]+)$', views.UploadView.as_view(), name='edit-project')
]
