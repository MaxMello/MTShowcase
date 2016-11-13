from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.AdminView.as_view(), name='home_admin'),
    url(r'^projects/$', views.ProjectListView.as_view(), name='project_list'),
    url(r'^backoffice/', admin.site.urls),
]
