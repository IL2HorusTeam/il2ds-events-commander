# -*- coding: utf-8 -*-
"""
Authentication-specific settings.
"""
from django.conf import settings

# Number of seconds for user to stay signed in after inactivity if he checked
# 'Remember me' during signing in. Default: 365 days
REMEMBER_ME_AGE = getattr(settings, 'REMEMBER_ME_AGE', 31536000)

# Number of days to wait for email confirmation
EMAIL_CONFIRMATION_DAYS = getattr(settings, 'EMAIL_CONFIRMATION_DAYS', 5)

SESSION_SIGN_UP_INFO_KEY = 'sign-up-info'
