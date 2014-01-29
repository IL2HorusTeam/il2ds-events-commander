# -*- coding: utf-8 -*-
"""
Commander's pilots service.
"""
from il2ds_middleware.service import PilotBaseService

from commander import log
from commander.service import CommanderServiceMixin


LOG = log.get_logger(__name__)


class PilotService(PilotBaseService, CommanderServiceMixin): # pylint: disable=R0904
    """
    Custom service for managing in-game pilots.
    """

    def user_joined(self, info):
        self.cl_client.chat_user(
            "Hello, {callsign}! Your IP is {ip}.".format(
            callsign=info['callsign'], ip=info['ip']),
            callsign=info['callsign'])
