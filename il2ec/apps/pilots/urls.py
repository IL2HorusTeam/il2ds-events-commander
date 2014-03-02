# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # -------------------------------------------------------------------------
    # API views
    # -------------------------------------------------------------------------
    url(r'^api/request-connection/$', 'pilots.views.api_request_connection',
        name='api-pilots-request-connection'),
)
