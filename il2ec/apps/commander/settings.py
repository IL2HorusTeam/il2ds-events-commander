# -*- coding: utf-8 -*-
"""
Settings for commander application.
"""
import os

from django.conf import settings
from il2ds_middleware.constants import REQUEST_TIMEOUT

#------------------------------------------------------------------------------
# Information about IL-2 Dedicated Server
#------------------------------------------------------------------------------

# Version to display for users
IL2_VERSION = getattr(settings, 'IL2_VERSION', '4.12.2')

# An iterable a containing sequence of present mods to display for users
IL2_PRESENT_MODS = getattr(settings, 'IL2_PRESENT_MODS', ())

# External address for game clients (users) to connect to
IL2_EXTERNAL_ADDRESS = getattr(settings, 'IL2_EXTERNAL_ADDRESS',
                               settings.HOSTNAME)

IL2_CONNECTION_DEFAULTS = {
    # Host name of interface for commander to connect to
    'host': 'localhost',
    # Server's console port for commander to connect to
    'cl_port': 20000,
    # Server's DeviceLink port for commander to interact with
    'dl_port': 10000,
}
IL2_CONNECTION_USER = getattr(settings, 'IL2_CONNECTION', {})
IL2_CONNECTION = dict(IL2_CONNECTION_DEFAULTS, **IL2_CONNECTION_USER)

# Path to server's config file for commander to read to
IL2_CONFIG_PATH = getattr(settings, 'IL2_CONFIG_PATH',
                          os.path.join('il2ds', 'confs.ini'))

# Path to server's events log file for commander to read to
IL2_EVENTS_LOG_PATH = getattr(settings, 'IL2_EVENTS_LOG_PATH',
                              os.path.join('il2ds', 'log', 'events.log'))

#------------------------------------------------------------------------------
# Commander settings
#------------------------------------------------------------------------------

# API listener settings
COMMANDER_API_DEFAULTS = {
    'host': '127.0.0.1',
    'port': 20001,
}
COMMANDER_API_USER = getattr(settings, 'COMMANDER_API', {})
COMMANDER_API = dict(COMMANDER_API_DEFAULTS, **COMMANDER_API_USER)

# Path to a file, where commander's PID will be stored. Use this file to
# stop commander by executing 'kill `cat /path/to/pid`'. If this value is set
# to 'None', then commander will run as non-daemon (it's OK for Windows)
COMMANDER_PID_FILE = getattr(settings, 'COMMANDER_PID_FILE', None)

# Logger settings
COMMANDER_LOG_DEFAULTS = {
    # Full path to a file, where commander's logs will be stored. If this value
    # is set to 'None', then commander will output logs to STDOUT
    'filename': None,
    # Logging level
    'level': 'INFO',
    # Format string that will be passed to strftime(). Default twisted
    # formatting will be used if 'None'
    'timeFormat': None,
    # Max size (in bytes) of a single log file
    'maxBytes': 1024 * 1024 * 10, # 10 MiB
    # Max number of log files
    'backupCount': 10,
}
COMMANDER_LOG_USER = getattr(settings, 'COMMANDER_LOG', {})
COMMANDER_LOG = dict(COMMANDER_LOG_DEFAULTS, **COMMANDER_LOG_USER)

# Timeouts (float values of seconds) for game server's console requests
# and DeviceLink requests
COMMANDER_TIMEOUT_DEFAULTS = {
    'console': REQUEST_TIMEOUT,
    'device_link': REQUEST_TIMEOUT,
}
COMMANDER_TIMEOUT_USER = getattr(settings, 'COMMANDER_TIMEOUT', {})
COMMANDER_TIMEOUT = dict(COMMANDER_TIMEOUT_DEFAULTS, **COMMANDER_TIMEOUT_USER)
