# -*- coding: utf-8 -*-
"""
Commander helping functions.
"""
import logging
import redis

from django.conf import settings

from commander.constants import KEY_COMMANDER_RUNNING


LOG = logging.getLogger(__name__)


def get_storage():
    """
    Get global storage, where information about running server and sommander
    is kept.
    """
    return redis.StrictRedis(host=settings.REDIS_HOST,
        port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DBS['COMMANDER'])


def is_commander_running(storage=None):
    """
    Tell if the commander is already running.
    """
    return False
    # storage = storage or get_storage()
    # return storage.exists(KEY_COMMANDER_RUNNING)
