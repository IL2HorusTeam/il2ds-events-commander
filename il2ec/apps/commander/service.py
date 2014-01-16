# -*- coding: utf-8 -*-
"""
Commander twisted services.
"""
import logging

from il2ds_middleware.parser import DeviceLinkParser
from il2ds_middleware.protocol import DeviceLinkClient

from twisted.application.service import MultiService, Service
from twisted.internet import defer
from twisted.internet.protocol import Factory

from commander import log
from commander import settings
from commander.protocol.async import APIServerProtocol, ConsoleClientFactory


LOG = log.get_logger(__name__)


class APIService(Service):
    """
    Service which manages TCP listener of incoming API requests.
    """
    listener = None

    def startService(self):
        factory = Factory()
        factory.commander = self.parent
        factory.protocol = APIServerProtocol

        from twisted.internet import reactor
        self.listener = reactor.listenTCP(settings.COMMANDER_API['port'],
            factory, interface=settings.COMMANDER_API['host'])

    def stopService(self):
        return defer.maybeDeferred(self.listener.stopListening)


class Commander(Service):
    """
    Main service which manages connections and main work.
    """
    client_factory = None

    cl_connector = None
    dl_connector = None

    dl_client = None

    def __init__(self):
        # Prepare DeviceLink client
        self.dl_client = DeviceLinkClient(
            address=(settings.IL2_CONNECTION['host'],
                     settings.IL2_CONNECTION['dl_port']),
            parser=DeviceLinkParser(),
            timeout_value=settings.COMMANDER_TIMEOUT['device_link'])

        # Prepare for connection with server
        self.client_factory = ConsoleClientFactory(
            # TODO: setup parser
            timeout_value=settings.COMMANDER_TIMEOUT['console'])

        # Prepare API listener
        self.api_service = APIService()
        self.api_service.parent = self

    @property
    def cl_client(self):
        """
        Get instance of concole protocol.
        """
        return self.client_factory.client

    def startService(self):
        """
        Start API requests listening port and UPD port for communicating with
        server via DeviceLink interface.

        This method is called by application.
        """
        self.api_service.startService()
        self.dl_client.on_start.addCallback(self.startConsoleConnection)

        from twisted.internet import reactor
        self.dl_connector = reactor.listenUDP(0, self.dl_client)

    def startConsoleConnection(self, unused):
        """
        Start reliable connection to game server's console with reconnectinon
        support.
        """
        self._update_connection_callbacks()

        from twisted.internet import reactor
        self.cl_connector = reactor.connectTCP(
            settings.IL2_CONNECTION['host'],
            settings.IL2_CONNECTION['cl_port'], self.client_factory)

    def stopService(self):
        """
        Stop everything. This method is called automatically when the reactor
        will be stopped.
        """
        dlist = []
        # Stop API listener
        dlist.append(self.api_service.stopService())

        # Stop DeviceLink UDP listener
        dlist.append(defer.maybeDeferred(self.dl_connector.stopListening))

        # Disconnect from game server's console, if connecting was started
        # or if connection was already established
        if self.cl_connector:
            self.client_factory.stopTrying()
            self.cl_connector.disconnect()

        # Return deferred to make reactor wait until everything is finished
        return defer.DeferredList(dlist)

    def stop(self):
        """
        Public method for stopping the whole commander.
        """
        from twisted.internet import reactor
        if reactor.running:
            reactor.stop()

    def _update_connection_callbacks(self):
        """
        Update callbacks which are called after the connection with game
        server's console is established or lost.
        """
        self.client_factory.on_connected.addCallback(self.on_connected)
        self.client_factory.on_disconnected.addErrback(self.on_disconnected)

    def on_connected(self, client):
        """
        This method is called after the connection with server's console is
        established. Main work starts from here.
        """

    def on_disconnected(self, reason):
        """
        This method is called after the connection with server's console is
        loas. Stop every work and clean up resources.
        """
        self._update_connection_callbacks()
