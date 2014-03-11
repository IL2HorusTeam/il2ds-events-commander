# -*- coding: utf-8 -*-
"""
Commander's missions service.
"""
from il2ds_middleware.service import MissionService as DefaultMissionService

from commander import log
from commander.service import CommanderServiceMixin


LOG = log.get_logger(__name__)


class MissionService(DefaultMissionService, CommanderServiceMixin):
    """
    Custom service for missions flow management.
    """

    @CommanderServiceMixin.radar_refresher
    def began(self, info=None):
        DefaultMissionService.began(self)

    @CommanderServiceMixin.radar_refresher
    def ended(self, info=None):
        DefaultMissionService.ended(self)

    def startService(self):
        DefaultMissionService.startService(self)

        from twisted.internet import reactor
        reactor.callLater(3, self.cl_client.mission_status)
