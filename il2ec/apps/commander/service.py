# -*- coding: utf-8 -*-
"""
Commander twisted services.
"""
import logging

from twisted.application.service import MultiService, Service
from twisted.internet import defer
from twisted.internet.protocol import Factory

from commander import log
from commander import settings
from commander.protocol.async import APIServerProtocol, ConsoleClientFactory


LOG = log.get_logger(__name__)


class APIService(Service):

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


class Commander(MultiService):

    connector = None
    factory = None

    def __init__(self):
        MultiService.__init__(self)

        # Prepare for connection with server
        self.factory = ConsoleClientFactory()
        self._update_connection_callbacks()

        # Prepare API listener
        api = APIService(self)
        self.addService(api)

    def startService(self):
        MultiService.startService(self)

        from twisted.internet import reactor
        self.connector = reactor.connectTCP(settings.IL2_CONNECTION['host'],
            settings.IL2_CONNECTION['cl_port'], self.factory)

    def stopService(self):
        dlist = []
        dlist.append(MultiService.stopService(self))

        d = self.factory.on_disconnected
        if d:
            dlist.append(d)

        self.factory.stopTrying()
        self.connector.disconnect()

        return defer.DeferredList(dlist)

    def on_connected(self, client):
        LOG.debug("yay! we are connected to dedicated server")

    def on_disconnected(self, client):
        LOG.debug("oops, connection with dedicated server was lost")
        self._update_connection_callbacks()

    def _update_connection_callbacks(self):
        self.factory.on_connected.addCallback(self.on_connected)
        self.factory.on_disconnected.addErrback(self.on_disconnected)

    def stop(self):
        from twisted.internet import reactor
        if reactor.running:
            reactor.stop()

    @property
    def client(self):
        return self.factory.client
