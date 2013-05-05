# -*- coding: utf-8 -*-
"""
Settings for website app.
"""
from django.conf import settings

import os

def init_settings():
    settings.TEMPLATE_DIRS += (
        os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'templates')),
    )
