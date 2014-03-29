# -*- coding: utf-8 -*-
"""
Commander's objects service.
"""
import tx_logging

from il2ds_middleware.service import MutedObjectsService
from commander.service import ClientServiceMixin


LOG = tx_logging.getLogger(__name__)


class ObjectsService(MutedObjectsService, ClientServiceMixin):
    """
    Custom service for mission objects management.
    """
