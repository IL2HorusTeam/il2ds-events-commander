# -*- coding: utf-8 -*-
"""
Settings for staging server.
"""
from il2ec.settings.base import *   # pylint: disable=W0614,W0401


VAR_ROOT = '/var/www/il2ec'
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')
STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'il2ec',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
    }
}

# WSGI_APPLICATION = 'il2ec.wsgi.dev.application'
