from django.conf.urls.static import static
from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^admin/settings/', include('livesettings.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admintools/', include('admin_tools.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('website.urls')),
)

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
