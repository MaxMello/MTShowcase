from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^search/$', views.Search.as_view(), name='search'),
    url(r'^about/$', views.About.as_view(), name="about")
]
