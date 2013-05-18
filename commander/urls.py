from django.contrib import admin
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns('',
    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^admin/settings/', include('livesettings.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('website.urls')),
)

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
