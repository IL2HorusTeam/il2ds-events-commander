# -*- coding: utf-8 -*-
"""
General-purpose context processors.
"""
import logging

from django.conf import settings as dj_settings

from website.helpers import get_project_name


LOG = logging.getLogger(__name__)


def settings(request): # pylint: disable=W0613
    """
    Inject application settings to template context.
    """
    return {'settings': dj_settings}


def language(request):
    """
    Inject current language name.
    """
    return {'LANGUAGE': dict(dj_settings.LANGUAGES).get(
                        request.LANGUAGE_CODE, request.LANGUAGE_CODE)}


def project_name(request):
    """
    Inject project name due to current language.
    """
    return {'PROJECT_NAME': get_project_name(request.LANGUAGE_CODE)}


def current_path(request):
    """
    Get path to current page without leading language code.
    """
    full_path = request.get_full_path()
    return {'CURRENT_PATH': full_path[full_path.index('/', 1):]}
