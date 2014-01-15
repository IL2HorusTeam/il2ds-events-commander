# -*- coding: utf-8 -*-
"""
Commander twisted services.
"""
import logging

from twisted.application import service
from twisted.internet.protocol import Factory

from commander import log
from commander import settings
from commander.protocol.async import APIServerProtocol


LOG = log.get_logger(__name__)


class APIService(service.Service):

    listener = None

    def __init__(self, commander):
        self.commander = commander

    def startService(self):
        factory = Factory()
        factory.commander = self.commander
        factory.protocol = APIServerProtocol

        from twisted.internet import reactor
        self.listener = reactor.listenTCP(settings.COMMANDER_API['port'],
            factory, interface=settings.COMMANDER_API['host'])

    def stopService(self):
        self.listener.stopListening()


class Commander(service.MultiService):

    def __init__(self):
        service.MultiService.__init__(self)
        api = APIService(self)
        self.addService(api)

    def stop(self):
        from twisted.internet import reactor
        if reactor.running:
            reactor.stop()
