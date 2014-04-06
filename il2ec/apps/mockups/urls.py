# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from mockups.views import IndexMissionRunningView


urlpatterns = patterns('',
    url(r'^index/mission-running/$', IndexMissionRunningView.as_view(),
        name='mockups-index-mission-running'),
)
