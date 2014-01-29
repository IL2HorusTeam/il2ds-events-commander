# -*- coding: utf-8 -*-
"""
Commander constant values.
"""
import json

from twisted.python.constants import ValueConstant, Values


class APICommandValueConstant(ValueConstant):
    """
    Extends base class by providing support to create a command with payload
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

