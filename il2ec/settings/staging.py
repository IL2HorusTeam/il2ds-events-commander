# -*- coding: utf-8 -*-
"""
Settings for staging platforms which serves project builds.
"""
# Import global settings to make it easier to extend settings.
from django.conf.global_settings import * # pylint: disable=W0614,W0401

from split_settings.tools import include, optional


include(
    'components/shared/paths.py',
    'components/staging/paths.py',

    'components/shared/base.py',
    'components/staging/base.py',
    optional('components/staging/private.py'),

    'components/shared/admin.py',

    scope=locals()
)
