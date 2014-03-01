# -*- coding: utf-8 -*-
"""
Settings for sessions and cookies shared by all environments.
"""
from django.template.defaultfilters import slugify


COOKIE_PREFIX = slugify(HOSTNAME)
if COOKIE_PREFIX:
    SESSION_COOKIE_NAME = '{0}-sessionid'.format(COOKIE_PREFIX)
    CSRF_COOKIE_NAME = 'csrftoken'
    LANGUAGE_SESSION_KEY = 'django_language'
    LANGUAGE_COOKIE_NAME = '{0}-{1}'.format(COOKIE_PREFIX,
                                            LANGUAGE_SESSION_KEY)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1 * 60 * 60 # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# Storing session in Redis
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_DB = REDIS_DBS['SESSIONS']
SESSION_REDIS_HOST = REDIS_HOST
SESSION_REDIS_PORT = REDIS_PORT

CSRF_COOKIE_HTTPONLY = True
