# -*- coding: utf-8 -*-
"""
Base settings shared by all environments.
"""
import os

from datetime import timedelta
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
# Generic project settings
#------------------------------------------------------------------------------

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

PROJECT_NAME = _("Your project name")

HOSTNAME = 'il2ec.example.com'
ALLOWED_HOSTS = [HOSTNAME, 'localhost', '127.0.0.1', ]

ADMINS = ()
SUPPORTERS = ()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Kiev'
USE_TZ = True

USE_I18N = True
USE_L10N = True

LANGUAGES_INFO = (
# -- code ------ name --- native name
    ('en', (_("English"), u"English")),
    ('ru', (_("Russian"), u"Русский")),
)
LANGUAGES = tuple([(code, name) for (code, (name, native)) in LANGUAGES_INFO])
LANGUAGE_CODE = 'en' # Main language code
LANGUAGE_CODES = tuple([code for (code, name) in LANGUAGES])

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

    # 3rd-party applications
    'django_extensions',
    'djcelery',
    'coffin',
    'compressor',
    'redis_sessions',
    'south',
    'transmeta',
    'il2ds_difficulty',

    # Project applications
    'auth_custom',
    'commander',
    'misc',
    'website',
)

#------------------------------------------------------------------------------
# Project URLS and media settings
#------------------------------------------------------------------------------

ROOT_URLCONF = 'il2ec.urls'

LOGIN_URL = '/sign-in/'
LOGOUT_URL = '/sign-out/'
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

    'website.context_processors.current_path',
    'website.context_processors.language_name',
    'website.context_processors.settings',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

STATICFILES_FINDERS += (
    'compressor.finders.CompressorFinder',
)

#------------------------------------------------------------------------------
# Middleware
#------------------------------------------------------------------------------

MIDDLEWARE_CLASSES += (
    # Disable caching for development
    # This middleware must be first on the list
    # 'django.middleware.cache.UpdateCacheMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

#------------------------------------------------------------------------------
# Auth / security
#------------------------------------------------------------------------------

AUTH_USER_MODEL = 'auth_custom.User'

AUTHENTICATION_BACKENDS = (
    'auth_custom.backends.CustomModelBackend',
)

#------------------------------------------------------------------------------
# Redis
#------------------------------------------------------------------------------

REDIS_DBS = {
    'SESSIONS': 1,
    'CACHE': 2,
    'COMMANDER': 3,
    'CELERY': 4,
    'CELERY_RESULTS': 5,
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''

#------------------------------------------------------------------------------
# Caching
#------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '{host}:{port}'.format(host=REDIS_HOST, port=REDIS_PORT),
        'OPTIONS': {
            'DB': REDIS_DBS['CACHE'],
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
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
            'maxBytes': 1024 * 1024 * 5, # 5 MiB
            'backupCount': 20,
            'filename': os.path.join(LOG_ROOT, 'il2ec-web.log'),
            'formatter': 'logsna',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
        'auth_custom': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
        'commander': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
        'misc': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
        'website': {
            'handlers': ['il2ec'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

#------------------------------------------------------------------------------
# Third party app settings
#------------------------------------------------------------------------------

# Celery ----------------------------------------------------------------------
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # Store results for 24 hours
CELERY_DISABLE_RATE_LIMITS = True
CELERY_TRACK_STARTED = True
CELERY_IMPORTS = ()
CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER

CELERYD_CONCURRENCY = 2
CELERYBEAT_MAX_LOOP_INTERVAL = 60
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

BROKER_URL = '{protocol}://{host}:{port}/{db}'.format(
    protocol='redis',
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DBS['CELERY'],
)
CELERY_RESULT_BACKEND = '{protocol}://{host}:{port}/{db}'.format(
    protocol='redis',
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DBS['CELERY_RESULTS'],
)
CELERYBEAT_SCHEDULE = {
    'delete-expired-sign-up-requests': {
        'task': 'auth_custom.tasks.delete_expired_sign_up_requests',
        'schedule': timedelta(hours=1),
    },
}

# Jinja2 ----------------------------------------------------------------------
JINJA2_EXTENSIONS = (
    'jinja2.ext.i18n',
    'jinja2.ext.with_',
    'compressor.contrib.jinja2ext.CompressorExtension',
)

JINJA2_TEMPLATE_DIRS = TEMPLATE_DIRS

JINJA2_DISABLED_APPS = (
    'admin',
)
JINJA2_DISABLED_TEMPLATES = (
    r'admin/',
)

JINJA2_TEMPLATE_LOADERS = TEMPLATE_LOADERS

# Django compressor -----------------------------------------------------------
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = ()
COMPRESS_CSS_FILTERS = ()

#------------------------------------------------------------------------------
# Commander settitngs
#------------------------------------------------------------------------------
IL2_VERSION = '4.12.2'
IL2_EXTERNAL_ADDRESS = HOSTNAME

IL2_SERVER_PATH = "path to your IL-2 DS"
IL2_CONFIG_PATH = os.path.join(IL2_SERVER_PATH, 'confs.ini')
IL2_EVENTS_LOG_PATH = os.path.join(IL2_SERVER_PATH, 'log', 'events.log')

IL2_CONNECTION = {
    'host': 'Your local host',
    'cl_port': 20000,
    'dl_port': 10000,
}

COMMANDER_PID_FILE = os.path.join(PROJECT_DIR, 'il2ec-daemon.pid')
COMMANDER_API = {
    'host': '127.0.0.1',
    'port': 20001,
}
COMMANDER_LOG = {
    'filename': os.path.join(LOG_ROOT, 'il2ec-daemon.log'),
    'level': "DEBUG",
}
