# -*- coding: utf-8 -*-
import simplejson as json

from il2ds_middleware.constants import REQUEST_TIMEOUT
from il2ds_middleware.parser import ConsolePassthroughParser
from il2ds_middleware.protocol import ConsoleClient as DefaultConsoleClient

from twisted.internet import defer
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineOnlyReceiver

from commander import log
from commander.constants import API_OPCODE
from commander.protocol.requests import (REQ_KICK_CALLSIGN, REQ_KICK_NUMBER,
    REQ_USERS_ALL, )


LOG = log.get_logger(__name__)


class APIServerProtocol(LineOnlyReceiver):
    """
    Twisted implementation of commander-side version of protocol for
    communicating with commander from the outside world.
    """
    def __init__(self):
        self.handlers = {
            API_OPCODE.QUIT: self.on_quit,
        }

    def lineReceived(self, line):
        peer = self.transport.getPeer()

        try:
            code_value, payload = tuple(json.loads(line))
        except Exception as e:
            LOG.error(
                "Failed to decode JSON from {host}:{port} in request "
                "\"{request}\": {err}".format(host=peer.host, port=peer.port,
                                              request=line, err=unicode(e)))
            self.transport.loseConnection()
            return
        try:
            opcode = API_OPCODE.lookupByValue(code_value)
        except ValueError as e:
            LOG.error("Failed to parse opcode '{code}' from {host}:{port} in "
                      "request \"{request}\"".format(code=code_value,
                      host=peer.host, port=peer.port, request=line))
            self.transport.loseConnection()
            return

        handler = self.handlers.get(opcode)
        if handler is None:
            LOG.error("No handler for opcode {opcode}!".format(opcode=opcode))
        else:
            handler(payload)

    def on_quit(self, _):
        self.factory.root_service.stop()


class ConsoleClient(DefaultConsoleClient):

    # FUTURE: merge into 'il2-ds-middleware' library.

    def kick_callsign(self, callsign):
        """
        Kick user by callsign.

        Input:
        `callsign` # callsign of the user to be kicked
        """
        self.sendLine(REQ_KICK_CALLSIGN.format(callsign))

    def kick_number(self, number):
        """
        Kick user by number, assigned by server (execute 'user' on server or
        press 'S' in game to see user numbers).

        Input:
        `number`  # number of the user to be kicked
        """
        self.sendLine(REQ_KICK_NUMBER.format(number))

    def kick_all(self, max_count):
        """
        Kick everyone from server.

        Input:
        `max_count`  # maximal possible number of users on server. See
                     # 'NET/serverChannels' in 'confs.ini' for this value
        """
        for i in range(max_count):
            # Kick 1st user in cycle. It's important to kick all of the users.
            # Do not rely on 'user_count' method in this situation: number
            # of users may change between getting current user list and kicking
            # the last user. It's OK if number of users will decrease, but if
            # it will increase, then someone may not be kicked. There is still
            # a little chance that someone will connect to server during
            # kicking process, but nothing can be done with this due to current
            # server functionality.
            self.kick_number(1)

    @defer.inlineCallbacks
    def user_count(self):
        """
        Get count users of connected users.
        Returns deferred.
        """
        strings = yield self._request_user_table()
        defer.returnValue(len(strings) - 1) # '1' is for user table's header

    def _request_user_table(self):
        """
        Request output from 'user' command.
        Returns deferred, which is invoked with server output strings
        containing users table. E.g.:

        " N       Name           Ping    Score   Army        Aircraft"
        " 1      oblalex          3       0      (0)None             "
        """
        return self._send_request(REQ_USERS_ALL)


class ConsoleClientFactory(ReconnectingClientFactory):
    """
    Factory for building server console's client protocols.
    """

    """
    Client's protocol class.
    """
    protocol = ConsoleClient

    """
    Parser instance which will be passed to client's protocol. Instance of
    'ConsolePassthroughParser' will be used if this value is not specified.
    """
    parser = None

    """
    Float value for server requests timeout in seconds which will be passed to
    client's protocol. 'REQUEST_TIMEOUT' will be used if this value is not
    specified.
    """
    request_timeout = None

    """
    Client's protocol instance placeholder.
    """
    client = None

    """
    Deferred, which will be invoked after the connection with server is
    established.
    """
    on_connected = None

    """
    Deferred, which will be invoked after the connection with server is lost.
    'on_connected' and 'on_disconnected' deferreds will be recreated before
    invocation of this deferred, so you will need to update your callbacks for
    connection and disconnection during processing this deferred's callback.
    """
    on_disconnected = None

    def __init__(self, parser=None, timeout_value=None):
        """
        Optional input:
        `parser`        : an object implementing IConsoleParser interface
        `timeout_value` : float value for server requests timeout in seconds
        """
        self.parser = parser
        self.timeout_value = timeout_value
        self._update_deferreds()

    def buildProtocol(self, addr):
        """
        Create a single protocol for communicating with game server's console.
        """
        client = ReconnectingClientFactory.buildProtocol(self, addr)
        client.parser = self.parser or ConsolePassthroughParser()
        client.timeout_value = self.timeout_value or REQUEST_TIMEOUT
        self.client = client
        return self.client

    def clientConnectionMade(self, client):
        self.resetDelay()
        LOG.debug("Connection successfully established")
        # Invoke callback and tell that connection was successfully established
        if self.on_connected is not None:
            d, self.on_connected = self.on_connected, None
            d.callback(client)

    def clientConnectionFailed(self, connector, reason):
        if self.continueTrying:
            LOG.error("Failed to connect to server: {0}".format(
                      unicode(reason.value)))
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        d, self.on_disconnected = self.on_disconnected, None
        if self.continueTrying == 0:
            LOG.debug("Connection with server was closed.")
            # Invoke callback and tell that connection was closed cleanly
            if d:
                d.callback(None)
        else:
            LOG.error("Connection with server is lost: {0}".format(
                      unicode(reason.value)))
            self._update_deferreds()
            # Invoke callback and tell that connection was lost
            if d:
                d.errback(reason)
            ReconnectingClientFactory.clientConnectionLost(
                self, connector, reason)

    def _update_deferreds(self):
        self.on_connected = defer.Deferred()
        self.on_disconnected = defer.Deferred()
