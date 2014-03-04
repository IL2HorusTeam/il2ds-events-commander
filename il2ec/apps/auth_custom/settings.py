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

# Length of password for connecting to game server
CONNECTION_PASSWORD_LENGTH = getattr(settings, 'CONNECTION_PASSWORD_LENGTH', 5)

# Number of password requests to send to user before kick from game server
CONNECTION_PASSWORD_REQUESTS_COUNT = getattr(settings,
    'CONNECTION_PASSWORD_REQUESTS_COUNT', 10)

# Period (in seconds) of password requests
CONNECTION_PASSWORD_REQUESTS_PERIOD = getattr(settings,
    'CONNECTION_PASSWORD_REQUESTS_PERIOD', 10)
