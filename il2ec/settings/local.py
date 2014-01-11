# -*- coding: utf-8 -*-
"""
Settings for local development server.
"""
from il2ec.settings.base import *   # pylint: disable=W0614,W0401


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'il2ec',
        'USER': 'vagrant',
        'PASSWORD': 'qwerty',
        'HOST': 'localhost',
        'PORT': '', # use default
    }
}

# ROOT_URLCONF = 'il2ec.urls.local'
# WSGI_APPLICATION = 'il2ec.wsgi.local.application'
