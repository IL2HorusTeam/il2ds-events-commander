# -*- coding: utf-8 -*-
"""
Commander constant values.
"""
import json

from twisted.python.constants import ValueConstant, Values


class APICommandValueConstant(ValueConstant):
    """
    Extends base class by providing support for creating a command with payload
    for commander's API.
    """
    def to_request(self, payload=None):
        """
        Make API command with payload and convert it to request in JSON format,
        so it can be sent to commander.
        """
        return json.dumps((self.value, payload, ))


class APIOpcode(Values):
    """
    Constants representing operation codes for commander API.
    """
    # Stop commander and quit it.
    QUIT = APICommandValueConstant(1)


# A symbol or string used to identify user command and separate it's arguments
USER_COMMAND_DELIMITER = '<'


class UserCommandValueConstant(ValueConstant):
    """
    Extends base class by providing support for creating a command for user.
    """
    def render(self, *args):
        chunks = ['', self.value]
        chunks.extend([unicode(x) for x in args])
        return USER_COMMAND_DELIMITER.join(chunks)


class UserCommand(Values):
    """
    Commands which can be sent by users to server from game chat.
    """
    CONNECTION_INSTRUCTIONS = UserCommandValueConstant('pass')
