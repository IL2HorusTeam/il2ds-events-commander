# -*- coding: utf-8 -*-
"""
Settings for production platforms which serves real projects.
"""
# Import global settings to make it easier to extend settings.
from django.conf.global_settings import * # pylint: disable=W0614,W0401

from split_settings.tools import include, optional


include(
    'components/shared/paths.py',
    optional('components/production/paths.py'),

    'components/shared/base.py',
    optional('components/production/base.py'),

    'components/shared/sessions.py',
    'components/shared/admin.py',

    scope=locals()
)
