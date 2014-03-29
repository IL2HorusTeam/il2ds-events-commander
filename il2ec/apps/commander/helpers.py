# -*- coding: utf-8 -*-
"""
Commander helping functions.
"""
import socket
import tx_logging

from commander import settings
from commander.protocol.blocking import api_create_client_socket
from commander.sharing import (shared_storage, KEY_SERVER_RUNNING,
    KEY_SERVER_NAME, KEY_SERVER_LOCAL_ADDRESS, KEY_SERVER_USER_PORT,
    KEY_SERVER_CHANNELS, KEY_SERVER_DIFFICULTY, KEY_SERVER_UPDATE_TOKEN, )

from il2ds_difficulty import decompose_difficulty_to_tabs

from misc.helpers import current_time_hash


LOG = tx_logging.getLogger(__name__)


def is_server_running():
    """
    Tell whether game server is running. Values is read from shared storage.
    """
    return shared_storage.exists(KEY_SERVER_RUNNING)


def is_commander_running():
    """
    Tell whether commander is running. It is considered to be running if
    information about game server is present in the shared storage or if
    commander's API socket exists.
    """
    if is_server_running():
        return True
    try:
        s = api_create_client_socket()
    except socket.error:
        return False
    else:
        s.close()
        return True


def get_server_info():
    if not is_server_running():
        return None

    difficulty = int(shared_storage.get(KEY_SERVER_DIFFICULTY))
    return {
        'name': shared_storage.get(KEY_SERVER_NAME),
        'version': settings.IL2_VERSION,
        'mods': settings.IL2_PRESENT_MODS,
        'address': {
            'external': settings.IL2_EXTERNAL_ADDRESS,
            'local': shared_storage.get(KEY_SERVER_LOCAL_ADDRESS),
            'port': int(shared_storage.get(KEY_SERVER_USER_PORT)),
        },
        'channels': int(shared_storage.get(KEY_SERVER_CHANNELS)),
        'difficulty': decompose_difficulty_to_tabs(difficulty),
    }


def set_server_update_token():
    token = current_time_hash()
    shared_storage.set(KEY_SERVER_UPDATE_TOKEN, token)
    return token


def get_server_update_token():
    return shared_storage.get(KEY_SERVER_UPDATE_TOKEN) or \
           set_server_update_token()


def server_info_was_updated(update_token):
    return update_token != get_server_update_token()
