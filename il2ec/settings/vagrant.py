# -*- coding: utf-8 -*-
"""
Settings for local development server which runs under Vagrant.
"""
# Import global settings to make it easier to extend settings.
from django.conf.global_settings import * # pylint: disable=W0614,W0401

from split_settings.tools import include, optional


include(
    'components/shared/paths.py',
    'components/vagrant/paths.py',

    'components/shared/base.py',
    'components/vagrant/base.py',

    optional('components/vagrant/private.py'),

    'components/shared/sessions.py',
    'components/shared/admin.py',

    scope=locals()
)
