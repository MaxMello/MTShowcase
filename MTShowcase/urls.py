from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from . import settings
from .secrets import production


urlpatterns = [
    url(r'^', include('apps.authentication.urls')),
    url(r'^', include('apps.home.urls')),
    url(r'^project/', include('apps.project.urls')),
    url(r'^user/', include('apps.user.urls')),
    url(r'^admin/', include('apps.administration.urls')),
    url(r'^backoffice/', admin.site.urls),
]


if not production:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
