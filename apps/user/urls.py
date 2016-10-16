from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<member_id>[0-9]+)$', views.UserProfileView.as_view(), name='user_profile'),
    url(r'^settings/$', views.SettingAccountView.as_view(), name='settings-account'),
    url(r'^socials/$', views.UserSocialView.as_view(), name='settings-user-socials'),
    url(r'^password-change/$', views.SettingPasswordChangeView.as_view(), name='password-change'),
    url(r'^password-change-done/$', views.PasswordChangeDoneView.as_view(), name='password-change-done'),
    url(r'^privacy/$', views.PrivacyView.as_view(), name='settings-privacy')
]
