from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^u/(?P<unique_name>[a-zA-z0-9_\-]+)$', views.UserProfileView.as_view(), name='user_profile'),
    url(r'^me/settings/$', views.SettingAccountView.as_view(), name='settings-account'),

    url(r'^me/drafts/$', views.UserProjectDraftView.as_view(), name='user-project-drafts'),

    url(r'^me/socials/$', views.UserSocialView.as_view(), name='settings-user-socials'),
    url(r'^me/password_change/$', views.SettingPasswordChangeView.as_view(), name='password-change'),
    url(r'^me/password_change_done/$', views.PasswordChangeDoneView.as_view(), name='password-change-done'),
    url(r'^me/privacy/$', views.PrivacyView.as_view(), name='settings-privacy'),  # TODO: Integrate privacy view in projects view
    url(r'^me/projects/$', views.ProjectListView.as_view(), name='projects-list')
]
