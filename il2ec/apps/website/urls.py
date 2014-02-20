# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from website.views import IndexView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='website-index'),

    # -------------------------------------------------------------------------
    # API views
    # -------------------------------------------------------------------------
    url(r'^api/task/result/(?P<task_id>.+)/$',
        'website.views.api_task_result',
        name='api-website-task-result'),
)
