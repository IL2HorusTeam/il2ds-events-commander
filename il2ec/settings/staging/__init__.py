# -*- coding: utf-8 -*-
"""
Settings for staging server.
"""
import os

from il2ec.settings.base import * # pylint: disable=W0614,W0401
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
# Import personal data
#------------------------------------------------------------------------------

try:
    from il2ec.settings.staging.private import EMAIL_HOST_USER
except ImportError:
    EMAIL_HOST_USER = None
try:
    from il2ec.settings.staging.private import EMAIL_HOST_PASSWORD
except ImportError:
    EMAIL_HOST_PASSWORD = None
try:
    from il2ec.settings.staging.private import SECRET_KEY
except ImportError:
    SECRET_KEY = 'h7#gw(#))b@r8z)xcio_g*du&^pky_x0)atn&*naxf6nh0j8y#'
try:
    from il2ec.settings.staging.private import DATABASE_CREDENTIALS
except ImportError:
    DATABASE_CREDENTIALS = {}

#------------------------------------------------------------------------------
# Calculation of directories relative to the project module location
#------------------------------------------------------------------------------

VAR_ROOT = os.path.join(
    os.path.expanduser('~'), '.virtualenvs', 'il2ec', 'var')
LOG_ROOT = os.path.join(VAR_ROOT, 'log')

try:
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
except OSError:
    pass

#------------------------------------------------------------------------------
# Main project settings
#------------------------------------------------------------------------------

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': dict(DATABASE_CREDENTIALS, **{
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'il2ec',
        'HOST': 'localhost',
        'PORT': '', # use default
    }),
}

HOSTNAME = 'il2ec.staging'
PROJECT_NAME = _("IL-2 events commander staging")
GRAPPELLI_ADMIN_TITLE = _("{0} admin").format(PROJECT_NAME)

#------------------------------------------------------------------------------
# Media settings
#------------------------------------------------------------------------------

STATIC_ROOT = os.path.join(VAR_ROOT, 'static')
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

#------------------------------------------------------------------------------
# Email settings
#------------------------------------------------------------------------------

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = (
    ("Developers", EMAIL_HOST_USER),
)
SUPPORTERS = ADMINS

#------------------------------------------------------------------------------
# Sessions / cookies
#------------------------------------------------------------------------------

from django.template.defaultfilters import slugify

COOKIE_PREFIX = slugify(HOSTNAME)
if COOKIE_PREFIX:
    SESSION_COOKIE_NAME = '{0}-sessionid'.format(COOKIE_PREFIX)
    CSRF_COOKIE_NAME = 'csrftoken'
    LANGUAGE_SESSION_KEY = 'django_language'
    LANGUAGE_COOKIE_NAME = '{0}-{1}'.format(COOKIE_PREFIX,
                                            LANGUAGE_SESSION_KEY)

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

LOGGING.update({
    'handlers': {
        'il2ec': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5, # 5 MiB
            'backupCount': 20,
            'filename': os.path.join(LOG_ROOT, 'il2ec-web.log'),
            'formatter': 'logsna',
        },
    },
    'loggers': LOGGERS,
})

#------------------------------------------------------------------------------
# Miscellaneous project settings
#------------------------------------------------------------------------------

# Commander settitngs ---------------------------------------------------------
IL2_VERSION = '4.12.2'
IL2_EXTERNAL_ADDRESS = HOSTNAME

IL2_CONNECTION = {
    'host': 'il2ds-host',
    'cl_port': 20000,
    'dl_port': 10000,
}

IL2_SERVER_PATH = "YOUR_IL2_SERVER_PATH"
IL2_CONFIG_PATH = os.path.join(IL2_SERVER_PATH, 'confs.ini')
IL2_EVENTS_LOG_PATH = os.path.join(IL2_SERVER_PATH, 'log', 'events.log')

COMMANDER_API = {
    'host': '127.0.0.1',
    'port': 20001,
}
COMMANDER_PID_FILE = os.path.join(PROJECT_DIR, 'il2ec-daemon.pid')
COMMANDER_LOG = {
    'filename': os.path.join(LOG_ROOT, 'il2ec-daemon.log'),
    'level': 'ERROR',
    'maxBytes': 1024 * 1024 * 10, # 10 MiB
    'backupCount': 10,
}
