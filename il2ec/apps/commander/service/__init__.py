# -*- coding: utf-8 -*-
"""
Commander main services.
"""
import logging

from il2ds_middleware.parser import (ConsoleParser, DeviceLinkParser,
    EventLogParser, )
from il2ds_middleware.protocol import DeviceLinkClient
from il2ds_middleware.service import LogWatchingService

from twisted.application.service import MultiService, Service
from twisted.internet import defer
from twisted.internet.protocol import Factory

from commander import log
from commander import settings
from commander.protocol.async import APIServerProtocol, ConsoleClientFactory


LOG = log.get_logger(__name__)


class CommanderServiceMixin:
    """
    Mixin for commander services which provides gives ability to access
    console and DeviceLink clients directly within services.
    """
    @property
    def cl_client(self):
        return self.parent.cl_client

    @property
    def dl_client(self):
        return self.parent.dl_client


class CommanderService(MultiService, CommanderServiceMixin):
    """
    Service which puts together all working services. Works only when the
    connection with server's console is established.
    """
    pilots = None
    objects = None
    missions = None

    console_parser = None
    dl_parser = None
    log_parser = None

    def __init__(self):
        MultiService.__init__(self)

        # Init pilots service
        from commander.service.pilots import PilotService
        self.pilots = PilotService()
        self.pilots.setServiceParent(self)

        # Init objects service
        from commander.service.objects import ObjectsService
        self.objects = ObjectsService()
        self.objects.setServiceParent(self)

        # Init missions service with log watcher
        from commander.service.missions import MissionService
        log_watcher = LogWatchingService(settings.IL2_EVENTS_LOG_PATH)
        self.missions = MissionService(log_watcher)
        self.log_parser = EventLogParser(
            (self.pilots, self.objects, self.missions, ))
        log_watcher.set_parser(self.log_parser)
        self.missions.setServiceParent(self)

        # Init console and DeviceLink parsers
        self.console_parser = ConsoleParser((self.pilots, self.missions, ))
        self.dl_parser = DeviceLinkParser()

    def startService(self):
        MultiService.startService(self)
        # update redis
        # read settings

    def stopService(self):
        d = MultiService.stopService(self)
        # clean-up redis
        return d


class APIService(Service):
    """
    Service which manages TCP listener of incoming API requests.
    """
    listener = None

    def startService(self):
        factory = Factory()
        factory.root_service = self.parent
        factory.protocol = APIServerProtocol

        from twisted.internet import reactor
        self.listener = reactor.listenTCP(settings.COMMANDER_API['port'],
            factory, interface=settings.COMMANDER_API['host'])

    def stopService(self):
        return defer.maybeDeferred(self.listener.stopListening)


class RootService(Service):
    """
    Main service which manages connections and all main work.
    """
    dl_client = None

    def __init__(self):
        self.cl_connector = None
        self.dl_connector = None

        self.commander = CommanderService()
        self.commander.parent = self

        # Prepare DeviceLink client
        self.dl_client = DeviceLinkClient(
            address=(settings.IL2_CONNECTION['host'],
                     settings.IL2_CONNECTION['dl_port']),
            parser=self.commander.dl_parser,
            timeout_value=settings.COMMANDER_TIMEOUT['device_link'])

        # Prepare for connection with server
        self.client_factory = ConsoleClientFactory(
            parser=self.commander.console_parser,
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
        is stopped.
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

        if self.commander.running:
            dlist.append(self.commander.stopService())

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
        self.commander.startService()

    def on_disconnected(self, reason):
        """
        This method is called after the connection with server's console is
        lost. Stop every work and clean up resources.
        """
        self._update_connection_callbacks()
        return self.commander.stopService()
