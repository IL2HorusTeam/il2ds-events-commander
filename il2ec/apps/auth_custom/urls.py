# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url

from auth_custom.views import SignInView, SignUpRequestView


urlpatterns = patterns('',
    url(r'^sign-in/$', SignInView.as_view(),
        name='auth-custom-sign-in'),
    url(r'^sign-out/$', 'auth_custom.views.sign_out',
        name='auth-custom-sign-out'),

    url(r'^sign-up/request/$', SignUpRequestView.as_view(),
        name='auth-custom-sign-up-request'),
    url(r'^sign-up/(?P<email>.+@.+..+)/(?P<confirmation_key>\w+)$',
        'auth_custom.views.sign_up',
        name='auth-custom-sign-up'),

    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',
        'auth_custom.views.password_reset',
        name='auth-custom-password-reset'),

    url(r'^user/settings/$', 'auth_custom.views.user_settings',
        name='auth-custom-user-settings'),

    # -------------------------------------------------------------------------
    # API views
    # -------------------------------------------------------------------------
    url(r'^api/sign-up/$', 'auth_custom.views.api_sign_up',
        name='api-auth-custom-sign-up'),
    url(r'^api/remind-me/$', 'auth_custom.views.api_remind_me',
        name='api-auth-custom-remind-me'),
    url(r'^api/password/change/$', 'auth_custom.views.api_password_change',
        name='api-auth-custom-password-change'),
    url(r'^api/user/settings/general/$',
        'auth_custom.views.api_general_settings',
        name='api-auth-custom-general-settings'),

    url(r'^api/user/settings/username/$',
        'auth_custom.views.api_change_username',
        name='api-auth-custom-change-username'),
    url(r'^api/user/deactivate/$',
        'auth_custom.views.api_deactivate_account',
        name='api-auth-custom-deactivate-account'),
)
