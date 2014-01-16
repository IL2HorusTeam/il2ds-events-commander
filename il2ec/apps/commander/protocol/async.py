# -*- coding: utf-8 -*-
import simplejson as json

from il2ds_middleware.constants import REQUEST_TIMEOUT
from il2ds_middleware.parser import ConsolePassthroughParser
from il2ds_middleware.protocol import ConsoleClient

from twisted.internet import defer
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineOnlyReceiver

from commander import log
from commander.constants import API_OPCODE


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
        self.factory.commander.stop()


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
