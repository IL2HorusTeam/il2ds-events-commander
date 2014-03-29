# -*- coding: utf-8 -*-
"""
Commander as twisted application.
"""
import logging
import sys

from django.conf import settings
sys.path.insert(0, settings.APPS_ROOT)

from twisted.application import service
from twisted.python.log import ILogObserver
from twisted.python.logfile import LogFile

from tx_logging.observers import LevelFileLogObserver

from commander.service import RootService
from commander.settings import COMMANDER_LOG as LOG_SETTINGS


# Init logging ----------------------------------------------------------------
filename = LOG_SETTINGS['filename']
log_file = LogFile.fromFullPath(
    filename,
    rotateLength=LOG_SETTINGS['maxBytes'],
    maxRotatedFiles=LOG_SETTINGS['backupCount']
) if filename is not None else sys.stdout

log_level = getattr(logging, LOG_SETTINGS['level'])

observer = LevelFileLogObserver(log_file, log_level)
observer.timeFormat = LOG_SETTINGS['timeFormat']


# Init application ------------------------------------------------------------
application = service.Application("IL-2 Events Commander")
application.setComponent(ILogObserver, observer.emit)


# Init commander service ------------------------------------------------------
root_service = RootService()
root_service.setServiceParent(application)
