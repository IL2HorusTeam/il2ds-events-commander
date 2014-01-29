# -*- coding: utf-8 -*-
"""
Implement 'stop_commander' Django management command for stopping IL-2 DS
commander.
"""
import os
import signal

from django.core.management.base import BaseCommand

from commander import settings
from commander.constants import APIOpcode
from commander.protocol.blocking import api_send_noreply_message


class Command(BaseCommand):
    """
    A management command which stops IL-2 DS events commander.
    """

    help = "Stop IL-2 DS events commander"

    def handle(self, *args, **kwargs): # pylint: disable=W0613
        if settings.COMMANDER_PID_FILE is None:
            # Mostly for Windows only
            api_send_noreply_message(APIOpcode.QUIT.to_request())
        else:
            if not os.path.exists(settings.COMMANDER_PID_FILE):
                print "PID file {path} does not exist. Is daemon running?" \
                      .format(path=settings.COMMANDER_PID_FILE)
                return
            with open(settings.COMMANDER_PID_FILE, 'r') as pid_file:
                pid = pid_file.read().strip()
            try:
                os.kill(int(pid), signal.SIGTERM)
            except OSError as e:
                print "Failed to terminate daemon: {e}".format(e=unicode(e))



