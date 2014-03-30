# -*- coding: utf-8 -*-
"""
Commander's missions service.
"""
import tx_logging

from il2ds_middleware.service import MissionsService as DefaultMissionsService
from commander.service import ClientServiceMixin


LOG = tx_logging.getLogger(__name__)


class MissionsService(DefaultMissionsService, ClientServiceMixin):
    """
    Custom service for missions flow management.
    """

    @ClientServiceMixin.radar_refresher
    def began(self, info=None):
        DefaultMissionsService.began(self, info)

    @ClientServiceMixin.radar_refresher
    def ended(self, info=None):
        DefaultMissionsService.ended(self, info)

    def startService(self):
        DefaultMissionsService.startService(self)
        return self.cl_client.mission_status()
