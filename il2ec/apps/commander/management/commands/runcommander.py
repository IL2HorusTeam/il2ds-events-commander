# -*- coding: utf-8 -*-
"""
Implement 'runcommander' Django management command.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from commander.service import Commander


class Command(BaseCommand):
    """
    A management command which runs IL-2 DS events commander.
    """
    help = "Run IL-2 DS events commander"

    def handle(self, *args, **kwargs):
        from twisted.internet import reactor
        Commander().startService()
        reactor.run()
