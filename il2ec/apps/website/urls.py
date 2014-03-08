# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from website.views import IndexView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(),
        name='website-index'),
    url(r'^contact/$', 'website.views.contact',
        name='website-contact'),

    # -------------------------------------------------------------------------
    # API views
    # -------------------------------------------------------------------------
    url(r'^api/contact/$',
        'website.views.api_contact',
        name='api-website-contact'),
    url(r'^api/task/result/(?P<task_id>.+)/$',
        'website.views.api_task_result',
        name='api-website-task-result'),

    url(r'^api/server-info/$',
        'website.views.api_server_info',
        name='api-website-server-info-no-token'),
    url(r'^api/server-info/(?P<update_token>\w+)/$',
        'website.views.api_server_info',
        name='api-website-server-info'),
)
