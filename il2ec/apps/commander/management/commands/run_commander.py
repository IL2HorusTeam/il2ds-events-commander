# -*- coding: utf-8 -*-
"""
Implement 'run_commander' Django management command for starting IL-2 DS
commander.
"""
import sys
import os

from django.core.management.base import BaseCommand
from twisted.scripts.twistd import run

from commander import application
from commander import settings


class Command(BaseCommand):
    """
    A management command which runs IL-2 DS events commander.
    """
    help = "Run IL-2 DS events commander"

    def handle(self, *args, **kwargs):
        args = [
            '-y', os.path.join(os.path.dirname(application.__file__),
                               "application.py"),
        ]
        if settings.COMMANDER_PID_FILE is None:
            args.append('--nodaemon')
        else:
            args.extend(['--pidfile', settings.COMMANDER_PID_FILE])
        sys.argv[1:] = args
        run()
