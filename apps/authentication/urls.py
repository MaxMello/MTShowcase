from django.conf.urls import url
from .views import ActivationView, RegisterView, LoginView, LogoutView
from django.views.generic.base import TemplateView

urlpatterns = [

    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^register/$', RegisterView.as_view(), name='register'),

    url(r'^register/complete/$',
        TemplateView.as_view(template_name='authentication/register_complete.html'),
        name='activation_complete'),

    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='authentication/activation_complete.html'
        ),
        name='registration_activation_complete'),

    #url(r'^activate/(?P<activation_key>[-:\w]+)/$',
     url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
]
