# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^sign-in/$', 'auth.views.sign_in', name='auth-sign-in'),
)
