# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^login/$', 'auth.views.login', name='auth-login'),
)
