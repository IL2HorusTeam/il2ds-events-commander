# -*- coding: utf-8 -*-
"""
Settings for pilots application.
"""
from django.conf import settings


# Length of password for connecting to game server
PILOTS_PASSWORD_LENGTH = getattr(settings, 'PILOTS_PASSWORD_LENGTH', 5)

# Number of password requests to send to user before kick
PILOTS_PASSWORD_REQUESTS_COUNT = getattr(settings,
    'PILOTS_PASSWORD_REQUESTS_COUNT', 10)

# Period (in seconds) of password requests
PILOTS_PASSWORD_REQUESTS_PERIOD = getattr(settings,
    'PILOTS_PASSWORD_REQUESTS_PERIOD', 10)
