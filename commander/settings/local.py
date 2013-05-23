# -*- coding: utf-8 -*-
# Django settings for commander project.
from __future__ import unicode_literals

import os
import sys
import dj_database_url
import commander as project_module

from django.utils.translation import ugettext_lazy as _

#-------------------------------------------------------------------------------
#   Project's paths
#-------------------------------------------------------------------------------

PROJECT_DIR = os.path.dirname(os.path.realpath(project_module.__file__))
APPS_ROOT = os.path.join(PROJECT_DIR, 'apps')
LOG_ROOT = os.path.join(PROJECT_DIR, 'logs')

try:
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
except OSError:
    pass

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

sys.path.append(APPS_ROOT)

#-------------------------------------------------------------------------------
#   Connections
#-------------------------------------------------------------------------------

REDIS_DBS = {
    'CACHE': 1,
    'JOHNNY_CACHE': 2,
    'SESSIONS': 3,
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''

#-------------------------------------------------------------------------------
#   Django commons
#-------------------------------------------------------------------------------

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.config(
        default = os.environ.get('IL2_HORUS_COMMANDER_DB_URL'))
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('IL2_HORUS_COMMANDER_SECRET_TOKEN')

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _(u'English')),
    ('ru', _(u'Russian')),
)

DEFAULT_LANGUAGE = 1

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'commander.wsgi.application'

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',

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

    'django_extensions',
    'compressor',
    'xlivesettings',

    'commons',
    'website',
    'admin_custom',
    'game_server',
)

#-------------------------------------------------------------------------------
#   Grappelli
#-------------------------------------------------------------------------------

GRAPPELLI_INDEX_DASHBOARD = 'admin_custom.dashboard.CommanderIndexDashboard'
GRAPPELLI_ADMIN_TITLE = _(u"IL-2 Horus Commander Admin")

#-------------------------------------------------------------------------------
#   URLs, static and media
#-------------------------------------------------------------------------------

ROOT_URLCONF = 'commander.urls'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''


# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static_collected')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

#-------------------------------------------------------------------------------
#   Templates
#-------------------------------------------------------------------------------

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',

    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.media',

    'website.context_processors.settings',
)

#-------------------------------------------------------------------------------
#   Jinja2
#-------------------------------------------------------------------------------

JINJA2_EXTENSIONS = (
    'jinja2.ext.i18n',
    'compressor.contrib.jinja2ext.CompressorExtension',
)

JINJA2_TEMPLATE_DIRS = TEMPLATE_DIRS

JINJA2_DISABLED_APPS = (
    'admin',
    'admindocs',
    'livesettings',
)

JINJA2_DISABLED_TEMPLATES = (
    r'admin/',
    r'admin/doc/',
    r'admin/settings/',
)

JINJA2_TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

#-------------------------------------------------------------------------------
#   Middlewares
#-------------------------------------------------------------------------------

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
)

#-------------------------------------------------------------------------------
#   Caching
#-------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{0}:{1}'.format(REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'DB': REDIS_DBS['CACHE'],
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'KEY_PREFIX': '',
        'TIMEOUT': 60 * 60,
    },
    'johnny_cache': {
        'BACKEND': 'johnny.backends.redis.RedisCache',
        'LOCATION': '{}:{}'.format(REDIS_HOST, REDIS_PORT),
        'JOHNNY_CACHE': True,
        'OPTIONS': {
            'DB': REDIS_DBS['JOHNNY_CACHE'],
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    }
}

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_il2hc'

CACHE_MIDDLEWARE_SECONDS = 1
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

#-------------------------------------------------------------------------------
#   Logging
#-------------------------------------------------------------------------------

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'logsna': {
            '()': 'logsna.Formatter',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'commander': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 20,
            'filename': os.path.join(LOG_ROOT, 'il2-horus-commander.log'),
            'formatter': 'logsna',
        },

    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'keyedcache': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'xlivesettings': {
            'handlers': ['commander'],
            'level': 'ERROR',
            'propagate': True,
        },
        'commons': {
            'handlers': ['commander'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'website': {
            'handlers': ['commander'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
