from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^(?P<project_id>[0-9]+)$', views.ProjectView.as_view(), name='project'),
    url(r'^upload/$', views.UploadView.as_view(), name='upload'),
]
