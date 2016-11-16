from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^p/(?P<base64_unique_id>[a-zA-z0-9\-_]{22})$', views.ProjectView.as_view(), name='project'),
    url(r'^me/project/new/$', views.UploadView.as_view(), name='new-project'),
    url(r'^me/project/(?P<base64_unique_id>[a-zA-z0-9\-_]{22})$', views.UploadView.as_view(), name='edit-project')
]
