# -*- coding: utf-8 -*-
"""
Commander's objects service.
"""
from il2ds_middleware.service import ObjectsBaseService

from commander import log
from commander.service import CommanderServiceMixin


LOG = log.get_logger(__name__)


class ObjectsService(ObjectsBaseService, CommanderServiceMixin):
    pass
