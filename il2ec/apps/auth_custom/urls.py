# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url

from auth_custom.views import SignUpRequestView


urlpatterns = patterns('',
    url(r'^sign-in/$', 'auth_custom.views.sign_in',
        name='auth-custom-sign-in'),
    url(r'^sign-out/$', 'auth_custom.views.sign_out',
        name='auth-custom-sign-out'),

    url(r'^sign-up/request/$', SignUpRequestView.as_view(),
        name='auth-custom-sign-up-request'),
    url(r'^sign-up/(?P<email>.+@.+..+)/(?P<confirmation_key>\w+)$',
        'auth_custom.views.sign_up',
        name='auth-custom-sign-up'),
    url(r'^sign-up/invoke/$', 'auth_custom.views.sign_up_invoke',
        name='auth-custom-sign-up-invoke'),
)
