# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url

from auth_custom.views import SignUpView, SignUpRequestView


urlpatterns = patterns('',
    url(r'^sign-in/$', 'auth_custom.views.sign_in', name='auth-custom-sign-in'),
    url(r'^sign-up/(?P<email>.+@.+..+)/(?P<key>\w+)$', SignUpView.as_view(),
                                                  name='auth-custom-sign-up'),
    url(r'^sign-up/request/$', SignUpRequestView.as_view(),
                               name='auth-custom-sign-up-request'),
)
