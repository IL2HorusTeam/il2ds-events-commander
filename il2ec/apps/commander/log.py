# -*- coding: utf-8 -*-
"""
Logger extensions for twisted.
"""
import logging

from twisted.python import log as tx_log
from twisted.python import util as tx_util


class Logger(object):
    """
    Wrapper of 'twisted.python.log.msg' function. Makes easy to set log levels
    and 'system' channel to log messages.
    """
    def __init__(self, name):
        self.name = name

    def critical(self, message):
        self._enlog(message, logging.CRITICAL)

    def error(self, message):
        self._enlog(message, logging.ERROR)

    def warning(self, message):
        self._enlog(message, logging.WARNING)

    def info(self, message):
        self._enlog(message, logging.INFO)

    def debug(self, message):
        self._enlog(message, logging.DEBUG)

    def _enlog(self, message, level):
        tx_log.msg(message, level=level, system=self.name)


class Manager(object):
    """
    Simplified version of 'logging.Manager'.
    """
    def __init__(self):
        self.loggers = {}

    def get_logger(self, name):
        """
        Get or create new logger with specisied name.
        """
        if not isinstance(name, basestring):
            raise TypeError("A logger name must be string or Unicode")
        if isinstance(name, unicode):
            name = name.encode("utf-8")
        logger = self.loggers.get(name)
        if logger is None:
            logger = Logger(name)
            self.loggers[name] = logger
        return logger


__manager = Manager()
get_logger = __manager.get_logger


class LevelFileLogObserver(tx_log.FileLogObserver):
    """
    Log messages observer. Has internal logging level threshold. Adds log level
    to output messages. See 'twisted.python.log.FileLogObserver'.
    """
    def __init__(self, f, level=logging.INFO):
        tx_log.FileLogObserver.__init__(self, f)
        self.log_level = level

    def emit(self, eventDict):
        """
        Extended base class' 'emit' method by log level support.
        """
        if eventDict['isError']:
            level = logging.ERROR
        elif 'level' in eventDict:
            level = eventDict['level']
        else:
            level = logging.INFO
        if level < self.log_level:
            return

        text = tx_log.textFromEventDict(eventDict)
        if text is None:
            return

        time_str = self.formatTime(eventDict['time'])
        fmt_dict = {
            'level': logging.getLevelName(level),
            'system': eventDict['system'],
            'text': text.replace("\n", "\n\t")
        }
        msg_str = tx_log._safeFormat("%(level)s:[%(system)s]:%(text)s\n",
                                     fmt_dict)

        tx_util.untilConcludes(self.write, time_str + " " + msg_str)
        tx_util.untilConcludes(self.flush)
