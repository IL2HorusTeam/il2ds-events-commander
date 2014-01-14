# -*- coding: utf-8 -*-
"""
Commander services.
"""
import logging

from django.conf import settings
from twisted.application import service
from twisted.internet.protocol import Factory

from commander.protocol import APIServerProtocol


LOG = logging.getLogger(__name__)


class APIService(service.Service):

    listener = None

    def __init__(self, commander):
        self.commander = commander

    def startService(self):
        factory = Factory()
        factory.commander = self.commander
        factory.protocol = APIServerProtocol

        from twisted.internet import reactor
        self.listener = reactor.listenTCP(settings.COMMANDER_API_PORT,
            factory, interface=settings.COMMANDER_API_HOST)

    def stopService(self):
        self.listener.stopListening()


class Commander(service.MultiService):

    def __init__(self):
        service.MultiService.__init__(self)
        api = APIService(self)
        self.addService(api)

    def stop(self):
        from twisted.internet import reactor
        reactor.stop()
