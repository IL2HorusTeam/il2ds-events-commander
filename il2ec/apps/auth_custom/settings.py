# -*- coding: utf-8 -*-
"""
Authentication-specific settings.
"""
from django.conf import settings

# Number of days to wait for email confirmation
EMAIL_CONFIRMATION_DAYS = getattr(settings, 'EMAIL_CONFIRMATION_DAYS', 5)
