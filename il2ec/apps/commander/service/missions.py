# -*- coding: utf-8 -*-
"""
Commander's missions service.
"""
from il2ds_middleware.service import MissionService as DefaultMissionService

from commander import log
from commander.service import CommanderServiceMixin


LOG = log.get_logger(__name__)


class MissionService(DefaultMissionService, CommanderServiceMixin):
    pass
