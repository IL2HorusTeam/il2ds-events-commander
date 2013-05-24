# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import platform

from datetime import datetime
from subprocess import Popen, PIPE
from threading import Thread, Lock
from time import sleep

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from config import get_server_path, get_server_restart_delay

#-------------------------------------------------------------------------------
# Defines
#-------------------------------------------------------------------------------

LOG = logging.getLogger(__name__)

PROCESS_STATUS_STOPPED = 'stpd'
PROCESS_STATUS_STARTING = 'strt'
PROCESS_STATUS_RUNNING = 'rnng'
PROCESS_STATUS_WAITING = 'wait'

PROCESS_STATUSES = {
    PROCESS_STATUS_STOPPED: _(u"stopped"),
    PROCESS_STATUS_STARTING: _(u"starting"),
    PROCESS_STATUS_RUNNING: _(u"running"),
    PROCESS_STATUS_WAITING: _(u"waiting for start"),
}

class ProcessManagerBox:
    pass

__m = ProcessManagerBox()
__m.mutex = Lock()
__m.process = None
__m.thread = None
__m.process_status = PROCESS_STATUS_STOPPED
__m.stop_requested = False
__m.restart_requested = False
__m.crash_count = 0
__m.work_time = None
__m.message = (None, None)
__m.status_update_time = None

#-------------------------------------------------------------------------------
# Global methods
#-------------------------------------------------------------------------------

def get_status():
    with __m.mutex:
        return __m.process_status

def get_status_update_time():
    with __m.mutex:
        return __m.status_update_time

def get_message():
    with __m.mutex:
        return __m.message

def get_crash_count():
    with __m.mutex:
        return __m.crash_count

def get_worktime():
    with __m.mutex:
        if __m.work_time:
            return datetime.now() - __m.work_time
        else:
            return None

def start(exe_path=None):
    exe_path = exe_path or get_server_path()
    with __m.mutex:
        if validate_status_for_start() == False:
            return
        if validate_path(exe_path) == False:
            return
        __m.thread = Thread(
            target = process_runner,
            args = (exe_path, ))
        __m.thread.daemon = True
        __m.thread.start()

def stop():
    LOG.debug("Stopping server")
    with __m.mutex:
        reset_message()
        if __m.process_status != PROCESS_STATUS_RUNNING:
            __m.message = (messages.ERROR, _(u"Server is not running"))
            LOG.error("not running")
            return False
        __m.stop_requested = True
        __m.process.kill()
    __m.thread.join()
    return True

def restart(exe_path=None):
    if stop():
        with __m.mutex:
            __m.restart_requested = True
        start(exe_path)

#-------------------------------------------------------------------------------
# Validators
#-------------------------------------------------------------------------------

def validate_status_for_start():
    reset_message()
    result = __m.process_status == PROCESS_STATUS_STOPPED
    if result == False:
        __m.message = (messages.WARNING, _(u"Process is already running or starting yet."))
        LOG.warning("already running or starting")
    return result

def validate_path(exe_path):
    reset_message()
    if os.path.isfile(exe_path) == False:
        __m.message = (messages.ERROR, _(u"Wrong path to server: \"%s\".") % exe_path)
        LOG.error("wrong server path %s" % exe_path)
        return False
    dir_path = os.path.dirname(os.path.abspath(exe_path))
    if validate_server_file(dir_path, "server.cmd") == False:
        return False
    if validate_server_file(dir_path, "confs.ini") == False:
        return False
    return True

def validate_server_file(dir_path, file_name):
    if os.path.isfile(os.path.join(dir_path, file_name)) == False:
        __m.message = (messages.ERROR, _(u"Server file \"%s\" not found.") % file_name)
        LOG.error("not found: %s" % file_name)
        return False

#-------------------------------------------------------------------------------
# Inner methods
#-------------------------------------------------------------------------------

def reset_message():
    __m.message = (None, None)

def process_runner(exe_path):
    if platform.system() == "Windows":
        start_args = []
    else:
        start_args = ["wine"]
    start_args.append(exe_path)
    while True:
        with __m.mutex:
            need_wait = __m.restart_requested
            __m.stop_requested = False
            __m.restart_requested = False

        if need_wait:
            do_wait()

        LOG.debug("starting server %s" % exe_path)
        set_status(PROCESS_STATUS_STARTING)

        __m.process = Popen(start_args, stdout=PIPE, stderr=PIPE)
        while True:
            line = __m.process.stdout.readline()
            if line.startswith("1>"):
                break

        LOG.debug("server started")
        set_status(PROCESS_STATUS_RUNNING)

        __m.process.wait()

        LOG.debug("server stopped")
        set_status(PROCESS_STATUS_STOPPED, True)

        with __m.mutex:
            if __m.stop_requested:
                break
            __m.crash_count += 1
        do_wait()

def do_wait():
    LOG.debug("waiting")
    set_status(PROCESS_STATUS_WAITING)
    sleep(get_server_restart_delay())
    set_status(PROCESS_STATUS_STOPPED)

def set_status(status, unset_work_time=False):
    with __m.mutex:
        __m.process_status = status
        __m.status_update_time = datetime.now()
        if unset_work_time:
            __m.work_time = None
        else:
            __m.work_time = datetime.now()
