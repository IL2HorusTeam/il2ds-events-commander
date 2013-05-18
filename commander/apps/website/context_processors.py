# -*- coding: utf-8 -*-
"""
Custom context processors for website application.
"""
from __future__ import unicode_literals

from django.conf import settings as setts

def settings(request):
    """
    Adds django settings to template context.
    """
    return {'settings': setts}
