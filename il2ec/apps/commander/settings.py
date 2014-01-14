# -*- coding: utf-8 -*-
"""
Settings for commander app.
"""
import os

from django.conf import settings


# Version to display for users
IL2_VERSION = getattr(settings, 'IL2_VERSION', '4.12.2')

# Host name for commander to connect to
IL2_LOCAL_HOST = getattr(settings, 'IL2_LOCAL_HOST', 'localhost')

# Host name for game clients (users) to connect to. Usually it's an external
# name or IP
IL2_USER_HOST = getattr(settings, 'IL2_USER_HOST', settings.HOSTNAME)

# Server's console port for commander to connect to
IL2_CONSOLE_PORT = getattr(settings, 'IL2_CONSOLE_PORT', 20000)

# Server's DeviceLink port for commander to connect to
IL2_DEVICE_LINK_PORT = getattr(settings, 'IL2_DEVICE_LINK_PORT', 10000)

# Path to server's config file for commander to read to
IL2_CONFIG_PATH = getattr(settings, 'IL2_CONFIG_PATH',
    os.path.join('il2ds', 'confs.ini'))

# Path to server's events log file for commander to read to
IL2_EVENTS_LOG_PATH = getattr(settings, 'IL2_EVENTS_LOG_PATH',
    os.path.join('il2ds', 'log', 'events.log'))

# Host for commander to listen commands on
COMMANDER_API_HOST = getattr(settings, 'COMMANDER_API_HOST', '127.0.0.1')

# Port for commander to listen commands on
COMMANDER_API_PORT = getattr(settings, 'COMMANDER_API_PORT', 20001)
