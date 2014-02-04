# -*- coding: utf-8 -*-
"""
Different helpers for website-related things.
"""
from django.conf import settings


def get_project_name(language_code=None):
    """
    Get project name from settings by specified or default language code.
    """
    return settings.PROJECT_NAME.get(language_code or settings.LANGUAGE_CODE)
