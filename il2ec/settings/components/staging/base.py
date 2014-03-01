# -*- coding: utf-8 -*-
"""
Base settings for staging environment.
"""
import os

from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
# Generic project settings
#------------------------------------------------------------------------------

HOSTNAME = 'il2events.servegame.com'
ALLOWED_HOSTS = ['*', ]

PROJECT_NAME = _("Awesome IL-2 events")
SECRET_KEY = 'h7#gw(#))b@r8z)xcio_g*du&^pky_x0)atn&*naxf6nh0j8y#'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'il2ec',
        'USER': 'db_user',               # redefine later
        'PASSWORD': 'db_user_password',  # redefine later
        'HOST': 'localhost',
        'PORT': '',                      # use default
    }
}

#------------------------------------------------------------------------------
# Email settings
#------------------------------------------------------------------------------

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'il2.horus.dev@gmail.com'
EMAIL_HOST_PASSWORD = None
EMAIL_PORT = 587

ADMINS = (
    ("Developers", EMAIL_HOST_USER),
)
SUPPORTERS = ADMINS

#------------------------------------------------------------------------------
# Commander
#------------------------------------------------------------------------------

IL2_CONNECTION = dict(IL2_CONNECTION, **{
    'host': 'il2ds-host',
})

IL2_SERVER_PATH = os.path.join(
    os.path.expanduser('~'), 'games', 'il2ds')
IL2_CONFIG_PATH = os.path.join(IL2_SERVER_PATH, 'confs.ini')
IL2_EVENTS_LOG_PATH = os.path.join(IL2_SERVER_PATH, 'log', 'events.log')

COMMANDER_LOG = {
    'filename': os.path.join(LOG_ROOT, 'il2ec-daemon.log'),
    'level': "DEBUG",
}
