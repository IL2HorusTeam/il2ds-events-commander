# -*- coding: utf-8 -*-
"""
Keys for sharing information about server via Redis.
"""
import redis

from django.conf import settings


KEY_SERVER_RUNNING = 'ds_running'
KEY_SERVER_NAME = 'ds_name'
KEY_SERVER_LOCAL_ADDRESS = 'ds_local_addr'
KEY_SERVER_USER_PORT = 'ds_user_port'
KEY_SERVER_CHANNELS = 'ds_channels'
KEY_SERVER_DIFFICULTY = 'ds_difficulty'


def get_storage():
    """
    Get global storage, where information about running server and sommander
    is kept.
    """
    return redis.StrictRedis(host=settings.REDIS_HOST,
        port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DBS['COMMANDER'])
