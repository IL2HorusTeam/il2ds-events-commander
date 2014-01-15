# -*- coding: utf-8 -*-
import logging
import socket

from commander import settings
from commander.protocol.async import APIServerProtocol


LOG = logging.getLogger(__name__)


class api_socket(socket.socket):
    """
    Raw socket for communication with commander. Enhances standart socket by
    providing ability to send lines to coomander and receive lines from it.
    """
    delimiter = APIServerProtocol.delimiter
    input_size = 4096

    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0,
                 _sock=None):
        super(api_socket, self).__init__(family, type, proto, _sock)
        self._line_reader = self._buffered_read_line()

    def _buffered_read_line(self):
        """
        Generator which provides buffered line reading from commander.
        """
        in_buffer = self.recv(self.input_size)
        while True:
            if self.delimiter in in_buffer:
                (line, in_buffer) = in_buffer.split(self.delimiter, 1)
                yield line
            else:
                chunk = self.recv(self.input_size)
                if not chunk:
                    break
                else:
                    in_buffer = in_buffer + chunk
        if in_buffer:
            yield in_buffer

    def read_line(self):
        """
        Read a line from commander with bufferization.
        """
        try:
            return next(self._line_reader)
        except StopIteration:
            # This will happen only if the connection was lost
            return None

    def send_line(self, line):
        """
        Send a string message with delimiter at the end to commander.
        """
        line = line + self.delimiter
        done = 0
        total = len(line)
        while done < total:
            try:
                sent = self.send(line[done:])
            except socket.error as e:
                LOG.warning("Connection with commander is broken: {err}"
                            .format(err=unicode(e)))
                break
            total = total + sent
        return done


def api_create_client_socket():
    """
    Create a blocking socket for interaction with commander via commander's API
    and make a connection.
    """
    try:
        s = api_socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        LOG.error("Failed to create client API socket: {err}".format(
                  err=unicode(e)))
        raise e
    try:
        s.connect((settings.COMMANDER_API['host'],
                   settings.COMMANDER_API['port']))
    except socket.error as e:
        LOG.error("Failed to connect to server API socket: {err}".format(
                  err=unicode(e)))
        raise e
    else:
        return s


def api_send_noreply_message(message, socket=None):
    """
    Send a noreply message to commander in blocking mode. Message is a string
    with JSON inside.
    """
    if socket:
        if not isinstance(socket, api_socket):
            raise ValueError(
                "Invalid instance of socket. api_socket must be passed.")
        socket.send_line(message)
    else:
        socket = api_create_client_socket()
        socket.send_line(message)
        socket.close()
