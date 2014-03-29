# -*- coding: utf-8 -*-
"""
Commander network asynchronous protocols and factories.
"""
import simplejson as json
import tx_logging

from twisted.protocols.basic import LineOnlyReceiver

from commander import stop_everything_n_quit
from commander.constants import APIOpcode


LOG = tx_logging.getLogger(__name__)


class APIServerProtocol(LineOnlyReceiver):
    """
    Twisted implementation of commander-side version of protocol for
    communicating with commander from the outside world.
    """
    def __init__(self):
        self.handlers = {
            APIOpcode.QUIT: self._on_quit,
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
            opcode = APIOpcode.lookupByValue(code_value)
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

    def _on_quit(self, dummy_payload):
        """
        Process 'quit' request.
        """
        stop_everything_n_quit()
