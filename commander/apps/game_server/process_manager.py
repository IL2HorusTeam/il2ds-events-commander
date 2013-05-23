# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import platform

from datetime import datetime
from subprocess import Popen, PIPE
from threading import Thread, Lock
from time import sleep

from django.utils.translation import ugettext_lazy as _

from xlivesettings import config_get

from config import (
    SERVER_GROUP_KEY,
    RESTART_DELAY_KEY
)

#-------------------------------------------------------------------------------
# Defines
#-------------------------------------------------------------------------------

LOG = logging.getLogger(__name__)

PROCESS_STATUS_STOPPED = 'stpd'
PROCESS_STATUS_STARTING = 'strt'
PROCESS_STATUS_RUNNING = 'rnng'

PROCESS_STATUSES = {
    PROCESS_STATUS_STOPPED: _(u"Process is stopped"),
    PROCESS_STATUS_STARTING: _(u"Process is starting"),
    PROCESS_STATUS_RUNNING: _(u"Process is running"),
}

class ProcessManagerBox:
    pass

__m = ProcessManagerBox()
__m.mutex = Lock()
__m.process = None
__m.thread = None
__m.process_status = PROCESS_STATUS_STOPPED
__m.stop_requested = False
__m.crash_count = 0
__m.start_time = None
__m.error_msg = None

#-------------------------------------------------------------------------------
# Global methods
#-------------------------------------------------------------------------------

def get_status():
    with __m.mutex:
        return __m.process_status

def get_error_msg():
    with __m.mutex:
        return __m.error_msg

def get_crash_count():
    with __m.mutex:
        return __m.crash_count

def get_uptime():
    with __m.mutex:
        if __m.process_status == PROCESS_STATUS_STOPPED:
            return None
        else:
            return datetime.now() - __m.start_time

def start(exe_path):
    with __m.mutex:
        if validate_status_for_start() == False:
            return
        if validate_path(exe_path) == False:
            return
        __m.stop_requested = False
        __m.thread = Thread(
            target = process_runner,
            args = (exe_path, ))
        __m.thread.daemon = True
        __m.thread.start()

def stop():
    LOG.debug("Stopping server")
    with __m.mutex:
        __m.error_msg = None
        if __m.process_status == PROCESS_STATUS_STOPPED:
            __m.error_msg = _(u"Server is not running")
            LOG.error(__m.error_msg)
            return False
        __m.stop_requested = True
        __m.process.kill()
    __m.thread.join()
    return True

def restart(exe_path):
    if stop():
        start(exe_path)

#-------------------------------------------------------------------------------
# Validators
#-------------------------------------------------------------------------------

def validate_status_for_start():
    __m.error_msg = None
    result = __m.process_status == PROCESS_STATUS_STOPPED
    if result == False:
        __m.error_msg = _(u"Process is already running or starting yet.")
        LOG.warning(__m.error_msg)
    return result

def validate_path(exe_path):
    __m.error_msg = None
    if os.path.isfile(exe_path) == False:
        __m.error_msg = _(u"Wrong path to server: \"%s\".") % exe_path
        LOG.error(__m.error_msg)
        return False
    dir_path = os.path.dirname(os.path.abspath(exe_path))
    if validate_server_file(dir_path, "server.cmd") == False:
        return False
    if validate_server_file(dir_path, "confs.ini") == False:
        return False
    return True

def validate_server_file(dir_path, file_name):
    if os.path.isfile(os.path.join(dir_path, file_name)) == False:
        __m.error_msg = _(u"Server file \"%s\" not found.") % file_name
        LOG.error(__m.error_msg)
        return False

#-------------------------------------------------------------------------------
# Process runner
#-------------------------------------------------------------------------------

def process_runner(exe_path):
    if platform.system() == "Windows":
        start_args = []
    else:
        start_args = ["wine"]
    start_args.append(exe_path)
    while True:
        LOG.debug("Starting server %s" % exe_path)
        with __m.mutex:
            __m.process_status = PROCESS_STATUS_STARTING
        __m.process = Popen(start_args, stdout=PIPE, stderr=PIPE)

        while True:
            line = __m.process.stdout.readline()
            if line.startswith("1>"):
                break

        LOG.debug("Server started")
        with __m.mutex:
            __m.process_status = PROCESS_STATUS_RUNNING
            __m.start_time = datetime.now()
        __m.process.wait()

        LOG.debug("Server stopped")
        with __m.mutex:
            __m.process_status = PROCESS_STATUS_STOPPED
            if __m.stop_requested:
                break
            __m.crash_count += 1
        sleep(config_get(SERVER_GROUP_KEY, RESTART_DELAY_KEY).value)
