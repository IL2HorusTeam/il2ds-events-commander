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
KEY_SERVER_UPDATE_TOKEN = 'ds_update_token'


class SharedStorage(redis.StrictRedis):

    def __init__(self):
        super(SharedStorage, self).__init__(host=settings.REDIS_HOST,
                                            port=settings.REDIS_PORT,
                                            password=settings.REDIS_PASSWORD,
                                            db=settings.REDIS_DBS['COMMANDER'])

    def update(self, kwargs):
        for key, value in kwargs.iteritems():
            self.set(key, value)

    def clear(self):
        self.flushdb()


shared_storage = SharedStorage()
