# -*- coding: utf-8 -*-

import logging

from django.conf import settings as app_settings


LOG = logging.getLogger(__name__)


def settings(request):
    """
    Inject application settings to template context.
    """
    return {'settings': app_settings}


def language(request):
    """
    Inject current language name.
    """
    return {'LANGUAGE': dict(app_settings.LANGUAGES).get(
                        request.LANGUAGE_CODE, request.LANGUAGE_CODE)}

def project_name(request):
    """
    Inject project name due to current language.
    """
    return {'PROJECT_NAME': app_settings.PROJECT_NAME.get(
                            request.LANGUAGE_CODE)}
