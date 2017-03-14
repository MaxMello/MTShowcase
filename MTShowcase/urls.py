from django.conf.urls import url, include
from django.conf.urls.static import static
import django.views.defaults
from . import settings
from .secrets import production
from django.conf.urls import handler404, handler500

handler404 = 'apps.home.views.handler404'
handler500 = 'apps.home.views.handler500'

urlpatterns = [
    url(r'^', include('apps.authentication.urls')),
    url(r'^', include('apps.home.urls')),
    url(r'^', include('apps.project.urls')),
    url(r'^', include('apps.user.urls')),
    url(r'^admin/', include('apps.administration.urls')),
    url(r'404/', handler404),
    url(r'500/', handler500)

]

if not production:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
