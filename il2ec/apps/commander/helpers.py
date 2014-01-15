# -*- coding: utf-8 -*-
"""
Commander helping functions.
"""
import redis

from django.conf import settings


def get_storage():
    """
    Get global storage, where information about running server and sommander
    is kept.
    """
    return redis.StrictRedis(host=settings.REDIS_HOST,
        port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DBS['COMMANDER'])
