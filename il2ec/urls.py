# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

from django.contrib import admin

from website.views import PageNotFoundView, ServerErrorView


admin.autodiscover()

handler404 = PageNotFoundView.as_view()
handler500 = ServerErrorView.as_view()

urlpatterns = patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns('',
    url(r'', include('auth_custom.urls')),
    url(r'', include('website.urls')),
    url(r'^mockups/', include('mockups.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
