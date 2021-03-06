from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^p/(?P<base64_unique_id>[a-zA-z0-9\-_]{22})$', views.ProjectView.as_view(), name='project'),
    url(r'^me/project/new/$', views.UploadView.as_view(), name='new-project'),
    url(r'^me/project/(?P<base64_unique_id>[a-zA-z0-9\-_]{22})$', views.UploadView.as_view(), name='edit-project'),
    url(r'^me/project/delete/(?P<base64_unique_id>[a-zA-z0-9\-_]{22})$', views.DeleteView.as_view(), name='delete-project'),
    url(r'^subjects_by_degree_program/(?P<degree_program_id>[0-9]+)$', views.get_subjects_by_degree_program, name='subjects-by-degree-program'),
    url(r'^user_choices_member_resp/$', views.MemberChoicesRespJsonResponseView.as_view(), name='member-choices-with-resp'),
    url(r'^supervisor_choices/$', views.SupervisorChoicesJsonResponseView.as_view(), name='supervisor-choices'),
    url(r'^add_content/(?P<content_type>[a-z]+)/$', views.AddContentJsonResponseView.as_view(), name='add-content'),
    url(r'^addcontentchoose$', views.ChooseContentJsonResponseView.as_view(), name="add-content-choose"),
    url(r'^addcontent_choices', views.ChooseContentChoicesJsonResponseView.as_view(), name="add-content-choices"),
    url(r'^input_templates/(?P<input_for>[a-z]+)$', views. FileInputTemplateJsonResponseView.as_view(), name="file-input-templates")
]

