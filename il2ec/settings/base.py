# -*- coding: utf-8 -*-
"""
Base settings shared by all environments.
"""
# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *   # pylint: disable=W0614,W0401
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
# Calculation of directories relative to the project module location
#------------------------------------------------------------------------------

import os
import sys
import warnings

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
HOSTNAME = 'il2ec.dev'
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
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'grappelli.dashboard',
    'grappelli',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'redis_sessions',
    'compressor',
    'django_extensions',
    'django_jinja',
    'south',
    'transmeta',

    'website',
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
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django_jinja.loaders.FileSystemLoader',
        'django_jinja.loaders.AppLoader',
    )),
)

STATICFILES_FINDERS += (
    'compressor.finders.CompressorFinder',
)

#------------------------------------------------------------------------------
# Middleware
#------------------------------------------------------------------------------

MIDDLEWARE_CLASSES += (
    'django.middleware.cache.UpdateCacheMiddleware', # This middleware must be first on the list

    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

#------------------------------------------------------------------------------
# Auth / security
#------------------------------------------------------------------------------

AUTHENTICATION_BACKENDS += (
    'django.contrib.auth.backends.ModelBackend',
)

#------------------------------------------------------------------------------
# Redis
#------------------------------------------------------------------------------

REDIS_DBS = {
    'SESSIONS': 1,
    'CACHE': 2,
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''

#------------------------------------------------------------------------------
# Sessions / cookies
#------------------------------------------------------------------------------

from django.template.defaultfilters import slugify

COOKIE_PREFIX = slugify(HOSTNAME)
if COOKIE_PREFIX:
    SESSION_COOKIE_NAME = '{0}-sessionid'.format(COOKIE_PREFIX)
    CSRF_COOKIE_NAME = 'csrftoken'
    LANGUAGE_SESSION_KEY = 'django_language'
    LANGUAGE_COOKIE_NAME = '{0}-{1}'.format(COOKIE_PREFIX, LANGUAGE_SESSION_KEY)

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE_AUTH_USER = 30 * 60  # 30 min
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Storing session in Redis
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_DB = REDIS_DBS['SESSIONS']
SESSION_REDIS_HOST = REDIS_HOST
SESSION_REDIS_PORT = REDIS_PORT

CSRF_COOKIE_HTTPONLY = True

#------------------------------------------------------------------------------
# Caching
#------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '{host}:{port}'.format(
                        host=REDIS_HOST,
                        port=REDIS_PORT,
                    ),
        'OPTIONS': {
            "DB": REDIS_DBS['CACHE'],
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'TIMEOUT': 60,
    },
}

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logsna': {
            '()': 'logsna.Formatter',
        }
    },
    'handlers': {
        'il2ec': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 20,
            'filename': os.path.join(LOG_ROOT, 'il2ec.log'),
            'formatter': 'logsna',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

#------------------------------------------------------------------------------
# Third party app settings
#------------------------------------------------------------------------------

# Django admin tools ----------------------------------------------------------
# ADMIN_TOOLS_INDEX_DASHBOARD = 'website.dashboard.AdminIndexDashboard'
# ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'website.dashboard.AdminAppIndexDashboard'
# ADMIN_TOOLS_MENU = 'website.menu.AdminMenu'
# ADMIN_TOOLS_THEMING_CSS = 'lib/admin_tools/css/theming.css'

# Django compressor -----------------------------------------------------------
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'sass --scss {infile} {outfile}'),
)
COMPRESS_CSS_FILTERS = ()

# Grappelli ------------------------------------------------------------------
GRAPPELLI_ADMIN_TITLE = _(u"IL-2 Events Commander")
GRAPPELLI_INDEX_DASHBOARD = 'website.dashboard.CustomIndexDashboard'

#------------------------------------------------------------------------------
# Miscellaneous project settings
#------------------------------------------------------------------------------
