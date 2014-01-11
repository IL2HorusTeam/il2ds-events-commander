"""Base settings shared by all environments"""
# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *   # pylint: disable=W0614,W0401
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
# Calculation of directories relative to the project module location
#------------------------------------------------------------------------------

import os
import sys
import il2ec as project_module

PROJECT_DIR = os.path.dirname(os.path.realpath(project_module.__file__))

PYTHON_BIN = os.path.dirname(sys.executable)
APPS_ROOT = os.path.join(PROJECT_DIR, 'apps')
VAR_ROOT = os.path.join('/var', 'virtualenvs', 'il2ec', 'var')
LOG_ROOT = os.path.join(VAR_ROOT, 'log')

try:
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
except OSError:
    pass

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

# Add apps root dir to pythonpath
sys.path.append(APPS_ROOT)

# Disable deprecation warnings for sake of clean output
warnings.filterwarnings("ignore", category=DeprecationWarning)

#------------------------------------------------------------------------------
# Generic Django project settings
#------------------------------------------------------------------------------

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Kiev'
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('en', _(u'English')),
    ('ru', _(u'Russian')),
)
# Main language code
LANGUAGE_CODE = 'en'
LANGUAGE_CODES = [code for (code, lang) in LANGUAGES]

# Make this unique, and don't share it with anybody.
# TODO: read SECRET_KEY from OS environment for dev settings
SECRET_KEY = '22mrx$5(7iik*hw!w-9x!7z78$f861**q#qv0bt7tewb1d-7+='

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'south',
    'transmeta',
    'compressor',
    'django_extensions',
)

#------------------------------------------------------------------------------
# Project URLS and media settings
#------------------------------------------------------------------------------

ROOT_URLCONF = 'il2ec.urls'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

#------------------------------------------------------------------------------
# Templates
#------------------------------------------------------------------------------

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS += (
)

#------------------------------------------------------------------------------
# Middleware
#------------------------------------------------------------------------------

MIDDLEWARE_CLASSES += (
)

#------------------------------------------------------------------------------
# Auth / security
#------------------------------------------------------------------------------

AUTHENTICATION_BACKENDS += (
)

#------------------------------------------------------------------------------
# Miscellaneous project settings
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Third party app settings
#------------------------------------------------------------------------------
