# -*- coding: utf-8 -*-
"""
Commander main services.
"""
import ConfigParser
import tx_logging

from collections import namedtuple

from django.utils.translation import ugettext as _

from il2ds_middleware.parser import (ConsoleParser, DeviceLinkParser,
    EventLogParser, )
from il2ds_middleware.protocol import (DeviceLinkClient,
    ReconnectingConsoleClientFactory, )
from il2ds_middleware.service import (LogWatchingService,
    ClientServiceMixin as DefaultClientServiceMixin, )

from twisted.application.service import MultiService, Service
from twisted.internet import defer, task
from twisted.internet.protocol import Factory

from commander import settings
from commander.helpers import set_server_update_token
from commander.protocol.async import APIServerProtocol
from commander.sharing import (shared_storage, KEY_SERVER_RUNNING,
    KEY_SERVER_NAME, KEY_SERVER_LOCAL_ADDRESS, KEY_SERVER_USER_PORT,
    KEY_SERVER_CHANNELS, KEY_SERVER_DIFFICULTY, )


LOG = tx_logging.getLogger(__name__)


class ClientServiceMixin(DefaultClientServiceMixin):

    @property
    def cl_client(self):
        return self.parent.cl_client

    @property
    def dl_client(self):
        return self.parent.dl_client


class CommanderService(MultiService, ClientServiceMixin):
    """
    Service which puts together all working services. Works only when the
    connection with server's console is established.
    """

    def __init__(self):
        MultiService.__init__(self)
        self.clear_shared_storage()

        # Place to store some of server confs values --------------------------
        self.confs = {}

        # Init pilots service -------------------------------------------------
        from commander.service.pilots import PilotsService
        pilots = PilotsService()
        pilots.setServiceParent(self)

        # Init objects service ------------------------------------------------
        from commander.service.objects import ObjectsService
        objects = ObjectsService()
        objects.setServiceParent(self)

        # Init missions service with log watcher ------------------------------
        from commander.service.missions import MissionsService
        log_watcher = LogWatchingService(settings.IL2_EVENTS_LOG_PATH)
        missions = MissionsService(log_watcher)
        log_parser = EventLogParser((pilots, objects, missions, ))
        log_watcher.set_parser(log_parser)
        missions.setServiceParent(self)

        # Init console and DeviceLink parsers ---------------------------------
        console_parser = ConsoleParser((pilots, missions, ))
        device_link_parser = DeviceLinkParser()

        # Group parsers and services ------------------------------------------
        self.parsers = namedtuple('commander_parsers',
            field_names=['console', 'device_link', 'log'])(
            console_parser, device_link_parser, log_parser)
        self.services = namedtuple('commander_services',
            field_names=['pilots', 'objects', 'missions'])(
            pilots, objects, missions)

    @defer.inlineCallbacks
    def startService(self):
        """
        Start commander service. This will start all main work to be done by
        subservices. Call this method after the connection with game console is
        successfully established.
        """
        self._load_server_config()
        self._share_data()
        yield self._greet_n_kick_all()
        yield MultiService.startService(self)

    def _load_server_config(self):
        """
        Load key server parameters from its 'confs.ini' configuration file.
        """
        config = ConfigParser.ConfigParser()
        config.read(settings.IL2_CONFIG_PATH)

        self.confs.update({
            'name': config.get('NET', 'serverName'),
            'user_port': config.getint('NET', 'localPort'),
            'channels': config.getint('NET', 'serverChannels'),
            'difficulty': config.getint('NET', 'difficulty'),
        })

    def _share_data(self):
        """
        Load information about game server into a shared storage.
        """
        shared_storage.update({
            KEY_SERVER_RUNNING: True,
            KEY_SERVER_NAME: self.confs['name'],
            KEY_SERVER_LOCAL_ADDRESS: self.cl_client.transport.getPeer().host,
            KEY_SERVER_USER_PORT: self.confs['user_port'],
            KEY_SERVER_CHANNELS: self.confs['channels'],
            KEY_SERVER_DIFFICULTY: self.confs['difficulty'],
        })
        set_server_update_token()

    @defer.inlineCallbacks
    def _greet_n_kick_all(self):
        """
        Kick every connected user, so information about them will be obtained
        after they reconnect. If there are some connected users, notify them
        about kick during 5 seconds.
        """
        count = yield self.cl_client.users_count()
        if not count:
            LOG.debug("No users to kick")
            defer.returnValue(None)

        def notify_users(seconds_left):
            """
            A callback which is called on every tick (1 per second). Notifies
            users about forced kick.
            """
            msg1 = _("Everyone will be kicked in {sec}...").format(
                     sec=seconds_left) if seconds_left else \
                   _("Everyone will be kicked NOW!")
            msg2 = _("Please, reconnect after kick.")
            self.cl_client.chat_all(u"{0} {1}".format(msg1, msg2))

        self.cl_client.chat_all(_("Hello everyone! This server is captured by "
                                  "IL-2 events commander."))

        LOG.debug("Greeting users with notification about kick")
        from twisted.internet import reactor
        for i in range(5, -1, -1):
            yield task.deferLater(reactor, 1, notify_users, i)

        LOG.debug("Kicking all users")
        yield self.cl_client.kick_all(self.confs['channels'], timeout=3)

    @defer.inlineCallbacks
    def stop(self, clean=False):
        """
        Overloaded base method for stopping commander service with all its
        subservices. Call this method when connection with server is lost or
        commander is going to exit.

        Input:
        clean:  'True' if commander was stopped manually, 'False' if connection
                with server was lost.
        """
        if clean:
            count = yield self.cl_client.users_count()
            if count:
                LOG.debug("Notifying users about quitting")
                self.cl_client.chat_all(
                    _("Commander is quitting. Goodbye everyone!"))

        yield MultiService.stopService(self)
        self.confs.clear()
        self.clear_shared_storage()

    def clear_shared_storage(self):
        shared_storage.clear()
        set_server_update_token()

    def stopService(self):
        """
        Overridden base method.
        """
        return self.stop()


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
    cl_client = None

    def __init__(self):
        self.cl_connector = None
        self.dl_connector = None

        self.commander = CommanderService()
        self.commander.parent = self

        # Prepare Device Link client ------------------------------------------
        self.dl_client = DeviceLinkClient(
            address=(settings.IL2_CONNECTION['host'],
                     settings.IL2_CONNECTION['dl_port']),
            parser=self.commander.parsers.device_link,
            timeout=settings.COMMANDER_TIMEOUT['device_link'])

        # Prepare for connection with server ----------------------------------
        self.client_factory = ReconnectingConsoleClientFactory(
            parser=self.commander.parsers.console,
            timeout=settings.COMMANDER_TIMEOUT['console'])

        # Prepare API listener ------------------------------------------------
        self.api_service = APIService()
        self.api_service.parent = self

    def startService(self):
        """
        Start API requests listening port and UPD port for communicating with
        server via DeviceLink interface.

        This method is called by application.
        """
        self.api_service.startService()
        self.dl_client.on_start.addCallback(self.start_console_connection)

        from twisted.internet import reactor
        self.dl_connector = reactor.listenUDP(0, self.dl_client)

    def start_console_connection(self, client): # pylint: disable=W0613
        """
        Start reliable connection to game server's console with reconnectinon
        support.
        """
        self._update_connection_callbacks()

        from twisted.internet import reactor
        self.cl_connector = reactor.connectTCP(
            settings.IL2_CONNECTION['host'],
            settings.IL2_CONNECTION['cl_port'], self.client_factory)

    @defer.inlineCallbacks
    def stopService(self):
        """
        Stop everything. This method is called automatically when the reactor
        is stopped.
        """
        # Stop commander service if running -----------------------------------
        if self.commander.running:
            yield self.commander.stop(clean=True)

        # Stop API listener ---------------------------------------------------
        yield self.api_service.stopService()

        # Stop Device Link UDP listener ---------------------------------------
        yield defer.maybeDeferred(self.dl_connector.stopListening)

        # Disconnect from game server's console, if connecting was started
        # or if connection was already established
        if self.cl_connector:
            self.client_factory.stopTrying()
            self.cl_connector.disconnect()

    def _update_connection_callbacks(self):
        """
        Update callbacks which are called after the connection with game
        server's console is established or lost.
        """
        if not self.client_factory.continueTrying:
            return
        self.client_factory.on_connecting.addCallback(self.on_connection_done)
        self.client_factory.on_connection_lost.addErrback(
            self.on_connection_lost)

    def on_connection_done(self, client):
        """
        This method is called after the connection with server's console is
        established. Main work starts from here.
        """
        self.cl_client = client
        self.commander.startService()

    def on_connection_lost(self, reason):
        """
        This method is called after the connection with server's console is
        lost. Stop every work and clean up resources.
        """
        self.cl_client = None
        self._update_connection_callbacks()
        return self.commander.stopService()
