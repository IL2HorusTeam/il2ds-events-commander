# -*- coding: utf-8 -*-
"""
Commander helping functions.
"""
import socket

from commander import log

from commander import settings
from commander.protocol.blocking import api_create_client_socket
from commander.sharing import (get_storage, KEY_SERVER_RUNNING,
    KEY_SERVER_NAME, KEY_SERVER_LOCAL_ADDRESS, KEY_SERVER_USER_PORT,
    KEY_SERVER_CHANNELS, KEY_SERVER_DIFFICULTY, )


LOG = log.get_logger(__name__)


def is_server_running(storage=None):
    storage = storage or get_storage()
    return storage.exists(KEY_SERVER_RUNNING)


def is_commander_running(storage=None):
    storage = storage or get_storage()
    if is_server_running(storage):
        return True
    try:
        s = api_create_client_socket()
    except socket.error as e:
        return False
    else:
        s.close()
        return True


def get_server_info(storage=None):
    storage = storage or get_storage()
    if not is_server_running(storage):
        return None
    return {
        'name'   : storage.get(KEY_SERVER_NAME),
        'version': settings.IL2_VERSION,
        'address': {
            'external': settings.IL2_EXTERNAL_ADDRESS,
            'local'   : storage.get(KEY_SERVER_LOCAL_ADDRESS),
            'port'    : int(storage.get(KEY_SERVER_USER_PORT)),
        },
        'channels'  : int(storage.get(KEY_SERVER_CHANNELS)),
        'difficulty': int(storage.get(KEY_SERVER_DIFFICULTY)),
    }
