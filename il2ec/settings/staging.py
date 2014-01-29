# -*- coding: utf-8 -*-
"""
Settings for staging server.
"""
from il2ec.settings.base import * # pylint: disable=W0614,W0401


VAR_ROOT = '/var/www/il2ec'
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')
STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'il2ec',
        'USER': 'vagrant',
        'PASSWORD': 'qwerty',
        'HOST': 'localhost',
        'PORT': '', # use default
    }
}
